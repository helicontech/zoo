# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.websocket
import re
import urllib
import os
import time
import pyuv
from threading import Thread
import signal
import logging
import subprocess
import sys, traceback
from core.helpers.decode import OutputDecoder
import json
from core.core import Core
import core.core
from datetime import timedelta
from datetime import datetime
from core.helpers.common import object_attrs_to_dict, kill_proc_tree, json_encode, json_decode

##TEST page for web sockets
from pyuv import thread as _thread


class TornadoConsole(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        """
        Возвращает экземпляр воркера, если оно создано.
        :rtype : Core
        """
        if not cls._instance:
            raise RuntimeError('worker is not created')
        return cls._instance

    @classmethod
    def create_instance(cls, *args):
        logging.debug('creating console wrapper')
        cls._instance = cls(*args)
        logging.debug('console wrapper has been created: {0}'.format(cls._instance))
        return cls._instance

    def __init__(self, *args):
        self.decoder = OutputDecoder()
        # TODO remove port from code
        self.main_loop = None
        self.buffer = {"buffer": {}}
        self.application_handlers = [
            (r"/console2", WebSocketHandler, {"configs": self.buffer})
        ]





# handler of processing connections
class WebSocketHandler(tornado.websocket.WebSocketHandler):

    # it doesnt want to work without it
    def check_origin(self, origin):
        return True

    # it doesnt want to work without it
    def initialize(self, configs):
        self.configs = configs

    # it doesnt want to work without it
    def open(self, *args):
        self.stream.set_nodelay(True)


    def create_console(self, request):
        if "create" in request:
            path = request["path"]
            console_obj = WebConsole.get_console(path)
            if console_obj is None:
                console_obj = WebConsole.create_console(request, None)
            else:
                logging.debug("this is an old cosole")
            console_obj.connection = self
            self.background_object = console_obj
            return True


    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        try:
            request = json_decode(message)
            if "create" in request:
                Result = self.create_console(request)
                self.write_message(json_encode({"status": Result}))
                return

            if "cancel" in request:
                logging.debug("cancel console")
                if self.background_object:
                    self.background_object.close()
                    self.close()
                return

            if "ping" in request:
                if "path" in request:
                    path = request["path"]
                    console_obj = WebConsole.get_console(path)
                    if console_obj:
                        self.writing_output(request)
                    else:
                        self.write_empty_pong()

                return

            if "ctrl_c" in request:
                console_instance = WebConsole.get_console(request["path"])
                if console_instance:
                    self.background_object.close()
                    self.close()
                return

            if "command" in request:
                console_instance = WebConsole.get_console(request["path"])
                if console_instance:
                    console_instance.execute(request['command'])
                    self.writing_output(request)
                else:
                    self.writing_console_down(request)
                return

        except Exception as e:
            error = traceback.format_exc()
            self.writing_error(error)

    def writing_console_down(self, obj):
        try:
            messages = []
            now_time = time.time()
            messages.append({"created": now_time, "message": "\n{0}\n".format(obj["command"]), "type": "stdout"})
            messages.append({"created": now_time, "message": "Zoo Web Console is Down\n Try recreate it", "type": "stderr"})
            result = {"status": True, "messages": messages}
            self.write_message(json_encode(result))
        except tornado.websocket.WebSocketClosedError:
            logging.debug("connection is closed")

    def writing_error(self, error):
        try:
            messages = []
            now_time = time.time()
            messages.append({"created": now_time, "message": error, "type": "stderr"})
            result = {"status": True, "messages": messages}
            self.write_message(json_encode(result))
        except tornado.websocket.WebSocketClosedError:
            logging.debug("connection is closed")


    def write_empty_pong(self):
        try:
            self.write_message(json_encode({"status": False}))
        except tornado.websocket.WebSocketClosedError:
            logging.debug("connection is closed")


    # write logs to socket
    def writing_output(self, obj):
        try:
            # process socket connection if depends
            path = obj["path"]
            console_obj  = WebConsole.get_console(path)
            messages = []
            now_time = time.time()
            # get dict repr for json

            for item in console_obj.buffer:
                messages.append({"created": now_time, "message": item['msg'], "type": item['type']})

            console_obj.buffer = []
            if len(messages) > 0:
                result = {"status": True,
                          "messages": messages}
                self.write_message(json_encode(result))
            else:
                self.write_empty_pong()

        except tornado.websocket.WebSocketClosedError:
            logging.debug("connection is closed")

        return

    # just write something, when we are closed
    def on_close(self):
        logging.debug("closed")
        try:
            if self.background_object:
                self.background_object.schedule_cancel_console()
        except:
            traceback.print_exc(file=sys.stdout)
        # WebConsole.cancel_console(self.background_object)




# TODO add varios os supporting
class WebConsole(object):
    """
    реализация веб-консоли
    1 экземпляра

    после запуска проверяет активно ли соединение с клиентом, если он не опрашивал консоль в течении IDLE_INTERVAL, то надо все закрыть
    """

    _consoles = {}  # активные консоли. для разных узлов в дереве
    _mutex = _thread.Mutex()

    IDLE_INTERVAL = 30

    @classmethod
    def get_console(cls, path):
        """
        получить консоль для указанного пути. если нет - None
        :param path:
        :return: object
        """
        return cls._consoles.get(path, None)

    @classmethod
    def create_console(cls, request,  callback_exit):
        """
        если нет в активных. то создать WebConsole и добавить в активные, по указанному пути

        :param path:
        :return:
        """
        cls._mutex.lock()
        path = request["path"]
        if not path in cls._consoles:
            console = WebConsole(path, request.get('engine', None),  callback_exit)
            cls._consoles[path] = console

        cls._mutex.unlock()
        return cls._consoles[path]

    def __init__(self, path, engine, callback_exit):
        """
        подготовить окружение к запуску дочернего процесса
        нужно
        - загрузить .zoo
        - найти на каком энжайне он работает
        - найти энжайн
        - взять текущие переменные окружения
        - взять переменные окружения энжайна
        - взять переменные окружения .zoo
        - раскрыть все переменные окружения

        запустить дочерний процесс

        :param path:
        """
        self.updated = None
        self.path = path
        self.core = Core.get_instance()
        self.buffer = []
        self.env = os.environ.copy()
        self.physical_path = self.core.api.os.web_server.map_webserver_path(self.path)
        if self.physical_path:
            self.site_root = self.core.api.os.web_server.siteroot4path(self.physical_path)
            self.app_physical_path = self.core.api.os.web_server.find_app_physical_path(self.physical_path,
                                                                                        self.site_root)
            if self.app_physical_path:
                self.zoo_config = self.core.api.os.web_server.get_zoo_config(self.app_physical_path)

                # emulate zoo module variables
                self.env["INSTANCE_ID"] = "0"
                self.env["APPL_PHYSICAL_PATH"] = self.app_physical_path
                self.env["APPL_PHYSICAL_SHORT_PATH"] = self.core.api.os.shell.get_short_path_name(self.app_physical_path)
                self.env["APPL_VIRTUAL_PATH"] = self.app_physical_path
                self.env["APPL_ID"] = self.env["APPL_VIRTUAL_PATH"].replace("/", "")
                std_console = self.env.copy()
                if self.zoo_config:
                    try:
                        zoo_env = self.core.api.os.web_server.create_environment(self.zoo_config, std_console, engine)

                        self.env = zoo_env
                    except Exception as e:
                        logging.debug(" cant create environment from zoo file")
                        logging.debug(e)
                        logging.debug(traceback.format_exc())
                        notes = str(e) + "\n"

        # we try to create console porcess in any case of errors
        else:
            # IT'S IMPORTANT FRO SECURITY REASONS
            raise Exception("There is no settings for this path {0}".format(path))

        self.pipe_stdin = None
        self.pipe_stdout = None
        self.pipe_stderr = None
        self.proc = None
        self.connection = None
        self.callback_exit=callback_exit
        self.on_callback_exit=None
        self.__start_process()

    def add_output(self, data):
        self.buffer.append({"msg": data, "type": "stdout"})

    def add_stderr(self, data):
        self.buffer.append({"msg": data, "type": "stderr"})

    def __repr__(self):
        return 'WebConsole({0})'.format(self.path)

    def execute(self, command):
        self.pipe_stdin.write(command.encode())
        self.pipe_stdin.write(b"\r\n")

    def to_dict(self):
        return object_attrs_to_dict(self, ['path', 'physical_path'])


    def control_c(self):
        try:
           logging.debug("sending control+c  %i to %i" % (2, self.proc.pid))
           if self.on_callback_exit is not None:
                logging.debug("repeating")
                return


           self.on_callback_exit = lambda: self.__start_process()
           kill_proc_tree(self.proc.pid)
           logging.debug(" restart console")
        except:
            traceback.print_exc(file=sys.stdout)


    def __start_process(self):
        callbak_newdata=self.add_output
        callback_newerr = self.add_stderr
        callback_exit=self.callback_exit

        event_loop = core.core.core_event_loop

        stdio = []
        self.pipe_stdin = pyuv.Pipe(event_loop)
        self.pipe_stdout = pyuv.Pipe(event_loop)
        self.pipe_stderr = pyuv.Pipe(event_loop)
        # Создание пайпа для stdin. В pipewrite мы будем писать на нашем конце, а piperead передадим child-у
        (piperead, pipewrite) = os.pipe()

        self.pipe_stdin.open(pipewrite)

        stdio.append(pyuv.StdIO(fd=piperead, flags=pyuv.UV_INHERIT_FD))
        stdio.append(pyuv.StdIO(self.pipe_stdout, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
        stdio.append(pyuv.StdIO(self.pipe_stderr, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))

        job_callback_exit = lambda proc, exit_status, term_signal: WebConsole.process_exit(self,
                                                                                           exit_status, term_signal,
                                                                                           callback_exit)

        self.proc = pyuv.Process.spawn(event_loop,
                                       executable="cmd.exe",
                                       args=["cmd.exe"],
                                       cwd=self.physical_path,
                                       exit_callback=job_callback_exit,
                                       env=self.env,
                                       stdio=stdio)

        self.pipe_stdout.start_read(lambda handle, data, error: WebConsole.read_cb(self, handle, data,
                                                                                   error, callbak_newdata))
        self.pipe_stderr.start_read(lambda handle, data, error: WebConsole.read_cb(self, handle, data,
                                                                                   error, callback_newerr))
        self.on_callback_exit=None


    def close(self):
        logging.debug("closing we have lost him")
        # this statement is needed if we use it directly
        try:
            self.connection = None
            event_loop = core.core.core_event_loop
            pid = self.proc.pid
            path = self.path
            working_done = lambda errno: WebConsole.cancel_console(path)
            working_callable = lambda: kill_proc_tree(pid)
            event_loop.queue_work(working_callable, working_done)
        finally:
            logging.debug("unexcepted error during closing console")
            WebConsole.cancel_console(path)



    @staticmethod
    def close_after_delay(timer_handle, console_obj):
        timer_handle.stop()
        try:
            if console_obj.connection is None:
                console_obj.close()
                return
        except:
            logging.debug("oh now he is back")


    def schedule_cancel_console(console_obj):
        WebConsole._mutex.lock()
        if console_obj.connection is not None:
            console_obj.connection = None
            event_loop = core.core.core_event_loop
            callback = lambda timer_handle: WebConsole.close_after_delay(timer_handle, console_obj)
            timer = pyuv.Timer(event_loop)
            timer.start(callback, WebConsole.IDLE_INTERVAL, WebConsole.IDLE_INTERVAL)
        WebConsole._mutex.unlock()




    @staticmethod
    def process_exit(Console, exit_status, term_signal, callback=None):
        # stop reading all pipes and close it
        logging.debug("here exiting the console")
        try:

            logging.debug("Process of worker is stoped %d and term signal %d" % (exit_status, term_signal))
            if not Console.pipe_stdin.closed:
                logging.debug("close pipe  in %s" % (Console.pipe_stdin))
                Console.pipe_stdin.close()
            if not Console.pipe_stdout.closed:
                logging.debug("close pipe out  %s" % (Console.pipe_stdout))
                Console.pipe_stdout.close()
            if not Console.pipe_stderr.closed:
                logging.debug("close pipe err  %s" % (Console.pipe_stderr))
                Console.pipe_stderr.close()

            Console.pipe_stdin = None
            Console.pipe_stdout = None
            Console.pipe_stderr = None
            Console.proc = None
            if Console.on_callback_exit:
                Console.on_callback_exit()

        except:
            logging.error("Error has been occured during the closing fs pipes")
        finally:
            # send api request to update install yaml
            if callback:
                callback(exit_status)



    @staticmethod
    def read_cb(Console, handle, data, error, callbak_output):
        if data is None:
            return

        self = Console
        self.updated = time.time()
        if error is not None:
            logging.info('Pipe read  %s' % data)
            logging.error('Pipe read error %s: %s' % (error, pyuv.errno.strerror(error)))
        logging.debug("Received data: %s" % (data))

        if data is not None:
            callbak_output(data.decode(encoding='utf-8', errors='ignore'))


    @classmethod
    def cancel_console(cls, path):
        """
        хендлер. закрытия консоли
        :param console:
        """
        logging.debug('Canceling {0}'.format(path))
        if path in cls._consoles and cls._consoles[path].connection is None:
            del cls._consoles[path]






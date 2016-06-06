# -*- coding: utf-8 -*-

import os
import subprocess
import logging
from threading import Thread
import time

from web.helpers.http import HttpResponseNotAllowed, HttpResponseServerError
from core.api.util.streams import OutputReader

from core.core import Core
from core.helpers.common import object_attrs_to_dict
from web.helpers.json import json_response, json_request

"""
работа с web- консолью
WebConsole
 - создает cmd.exe с переменными окружения такими же как для сайта + зу модуль, с учетом .zoo файла, и выбраного энжайна
 - пренаправляет вызовы к этой консоли
 - читатет ответ
 - выводит на экран
"""

@json_response
def create(request):
    """
    Создать экземпляр веб-консоли
    консолей может быть несколько, но для каждого пути только 1

    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    req = json_request(request)
    path = req['path']
    console = WebConsole.create_console(path)
    return console.to_dict()


@json_response
def write(request):
    """
    записать в консоль строку, переданную в параметрах

    :param request:
    :return: :raise RuntimeError:
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    req = json_request(request)
    path = req['path']
    console = WebConsole.get_console(path)
    if not console:
        raise RuntimeError('Console for {0} is not created or closed.'.format(path))

    return console.write(req['data'] + '\r\n')


@json_response
def read(request):
    """
    прочитать порцию ответа из консоли

    :param request:
    :return: :raise RuntimeError:
    """
    path = request.GET['path']
    console = WebConsole.get_console(path)
    if not console:
        raise RuntimeError('Console for {0} is not created or closed.'.format(path))

    return console.read()


@json_response
def cancel(request):
    """
    убить дочерний процесс.

    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    req = json_request(request)
    path = req['path']
    console = WebConsole.get_console(path)
    if not console:
        http_body = 'console is not created for {0}'.format(path)
        return HttpResponseServerError(body=http_body)

    WebConsole.cancel_console(console)

    return {}


class WebConsole(object):
    """
    реализация веб-консоли
    1 экземпляра

    после запуска проверяет активно ли соединение с клиентом, если он не опрашивал консоль в течении IDLE_INTERVAL, то надо все закрыть
    """

    _consoles = {}  # активные консоли. для разных узлов в дереве

    IDLE_INTERVAL = 30

    @classmethod
    def get_console(cls, path):
        """
        получить консоль для указанного пути. если нет - None
        :param path:
        :return:
        """
        return cls._consoles.get(path, None)

    @classmethod
    def create_console(cls, path):
        """
        если нет в активных. то создать WebConsole и добавить в активные, по указанному пути

        :param path:
        :return:
        """
        if not path in cls._consoles:
            console = WebConsole(path)
            cls._consoles[path] = console

        return cls._consoles[path]

    def __init__(self, path):
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
        self.path = path
        self.core = Core.get_instance()
        self.physical_path = self.core.api.os.web_server.map_webserver_path(self.path)
        self.zoo_config = self.core.api.os.web_server.get_zoo_config(self.physical_path)
        self.env = os.environ.copy()
        # emulate zoo module variables
        self.env["INSTANCE_ID"] = "0"
        self.env["APPL_PHYSICAL_PATH"] = self.physical_path
        self.env["APPL_PHYSICAL_SHORT_PATH"] = self.core.api.os.shell.get_short_path_name(self.physical_path)
        self.env["APPL_VIRTUAL_PATH"] = self.path
        self.env["APPL_ID"] = self.env["APPL_VIRTUAL_PATH"].replace("/", "")

        if self.zoo_config:
            zoo_env = self.core.api.os.web_server.create_environment(self.zoo_config, self.env)
            self.env = zoo_env

        self.process = None

        self.pipe_stdin = None
        self.pipe_stdout = None
        self.pipe_stderr = None

        self.std_out = ""
        self.std_err = ""
        self.stdout_reader = None
        self.stderr_reader = None
        self.timestamp = 0
        self.start()




    def __repr__(self):
        return 'WebConsole({0})'.format(self.path)

    def to_dict(self):
        return object_attrs_to_dict(self, ['path', 'physical_path'])

    def start(self):
        """
        запустить дочерний процесс консоли
        self.env - переоперделенные переменные окружения
        read_output_thread - поток читатель из std_out
        check_idle_thread - поток, проверяет активное ли соединение,
                            JavaScript делает переодически запросы к консоли для получить новые буквы ответа,
                            и если давно небыло опроса, то пора выходить
        """
        self.process = subprocess.Popen(
            'cmd.exe',
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            bufsize=1,
            cwd=self.physical_path
        )

        self.stdout_reader = OutputReader(self.process.stdout)
        self.stderr_reader = OutputReader(self.process.stderr)

        read_output_thread = Thread(target=self.read_output)
        read_output_thread.daemon = True
        read_output_thread.start()

        check_idle_thread = Thread(target=self.check_idle_thread)
        check_idle_thread.daemon = True
        check_idle_thread.start()

    def read_output(self):
        """
        читать все что выдала консоль.
        запомнить в self.std_out, self.std_er

        """
        while True:
            if not self.process or self.process.poll() is not None:
                break

            out = self.stdout_reader.read_nowait()
            self.std_out += out

            err = self.stderr_reader.read_nowait()
            self.std_err += err
       #    logging.debug(" from output %s" % out)
            # if not out and not err:
            time.sleep(0.1)
        logging.debug('read_output_thread completed')

    def write(self, command):
        """
        просто записать строку в консоль

        :param command:
        :return:
        """
        logging.debug(command)
        self.process.stdin.write(str.encode(command))
        self.process.stdin.flush()

        self.timestamp = time.time()

        resp = {}
        return resp

    def read(self):
        """
        прочитать из консоли,
        кажется не используется

        :return:
        """
        out = self.std_out
        self.std_out = ''

        err = self.std_err
        self.std_err = ''
        logging.debug('ping connection: ')

        if out:
            logging.debug('stdout: {0}'.format(out))
        if err:
            logging.debug('stderr: {0}'.format(err))

        self.timestamp = time.time()

        return {
            'stdout': out,
            'stderr': err,
        }

    def check_idle_thread(self):
        """
        тело потока, проверка на активность клиента консоли
        вечный цикл
        если давно небыло запроса к консоли, то закрыть ее

        """
        self.timestamp = time.time()
        while True:
            time.sleep(10)
            if self.check_idle():
                break
        logging.debug('check_idle_thread completed')

    def check_idle(self):
        """
        поверить наступило ли условие для выхода
        если ппроцесс умер
        если небыло давно запросов в веб консоли

        :return:
        """
        logging.debug('check idle console')
        if not self.process or self.process.poll() is not None:
            return True
        if time.time() - self.timestamp >= self.IDLE_INTERVAL:
            # console is idle for IDLE_INTERVAL second
            logging.info('{0} is idle, close it'.format(self))
            WebConsole.cancel_console(self)
            return True
        return False

    def cancel(self):
        """
        убить процесс

        """
        self.process.terminate()
        self.process = None

    @classmethod
    def cancel_console(cls, console):
        """
        хендлер. закрытия консоли
        :param console:
        """
        logging.debug('Canceling {0}'.format(console))
        console.cancel()
        del cls._consoles[console.path]

    def update_env(self, env, env2):
        for (key, value) in env2.items():
            env[key.upper()] = os.path.expandvars(value)


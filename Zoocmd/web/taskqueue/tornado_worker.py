# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from tornado import gen
from core.models.database import PeeweeLogMessage as LogMessage
import re
import urllib
import os
import time
from queue import Queue

from core.models.database import TaskPeewee as Task
from core.models.database import JobPeewee as JobDataModel
from core.log_manager import LogManager
from core.task_manager import TaskManager

import logging
import subprocess
import sys
from core.helpers.decode import OutputDecoder
from core.helpers.common import json_encode, json_decode
from core.job import Job
import json
from core.core import Core
import core.core
from datetime import timedelta
from datetime import datetime


##TEST page for web sockets

Page = "<!DOCTYPE html>\
<html>\
    <head>\
    <meta charset=\"utf-8\">\
	<script type=\"text/javascript\">\
        function WebSocketTest() {\n\
            var messageContainer = document.getElementById(\"messages\");\n\
            if (\"WebSocket\" in window) {\n\
                messageContainer.innerHTML = \"WebSocket is supported by your Browser!\";\n\
                var ws = new WebSocket(\"ws://localhost:7798/socket/log?Id=123456789\");\n\
                ws.onopen = function() {\n\
                    ws.send(\"Message to send\");\n\
                };\n\
                ws.onmessage = function (evt) {\n\
                    var received_msg = evt.data;\n\
                    Prev = messageContainer.innerHTML ;\n\
                    messageContainer.innerHTML = Prev + received_msg;\n\
                    ws.send(\"one more\");\n\
                };\n\
                ws.onclose = function() {\n\
                    messageContainer.innerHTML = \"Connection is closed...\";\n\
                };\n\
            } else {\n\
                messageContainer.innerHTML = \"WebSocket NOT supported by your Browser!\";\n\
            }\n\
        }\n\
        </script>\
    </head>\
    <body>\
        <a href=\"javascript:WebSocketTest()\">Run WebSocket</a>\
        <div id=\"messages\" style=\"height:100%;background:black;color:white;\"></div>\
    </body>\
</html>"


# TODO rework working with LogMessage object
class TornadoWorker(object):
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
        logging.debug('creating worker instance')
        cls._instance = cls(*args)
        logging.debug('core created: {0}'.format(cls._instance))
        return cls._instance

    def __init__(self, *args):
        self.logger = None
        # deprecated
        self.decoder = OutputDecoder()
        # TODO remove port from code
        self.main_loop = tornado.ioloop.IOLoop.instance()
        self.pool = {"buffer": {}, "task": None}

        self.application_handlers = [
            (r"/socket/log", WebSocketHandler, {"configs": self.pool}),
            (r"/test", MainHandler, {"configs": self.pool})
        ]

    @staticmethod
    def start_new_task(task, user_proc_exit_cb=None, save_buffer=True):
        worker = TornadoWorker.get_instance()
        logging.debug("we have new job to start %s" % str(task))
        core = Core.get_instance()
        new_job = Job.create_job(task, core)
        logging.debug(new_job)

        if new_job.task_id not in worker.pool["buffer"]:
            worker.pool["buffer"][new_job.task_id] = []

        task.update(status=JobDataModel.STATUS_RUNNING)
        proc_exit_cb = None
        if user_proc_exit_cb:
            proc_exit_cb = lambda job, exit_code: TornadoWorker.process_finished(worker, job,
                                                                                 exit_code, user_proc_exit_cb)
        else:
            proc_exit_cb = lambda job, exit_code: TornadoWorker.process_finished(worker, job, exit_code)

        read_logs = None
        if save_buffer:
            read_logs = lambda lines, log_level: TornadoWorker.async_read_logs(worker, new_job, lines, log_level)
        else:
            read_logs = lambda lines, log_level: TornadoWorker.async_write_logs2stdout(worker, new_job,
                                                                                       lines, log_level)
        job_log_manager = LogManager(core)

        new_job.start_job_async(job_log_manager, proc_exit_cb, read_logs)

    # new message to the stack and write it to socket
    def put_new_message(self, new_msg):
        self.pool["buffer"][new_msg.task_id].append(new_msg)
        # save at database
        if new_msg.job_object is not None:
            new_msg.job = new_msg.job_object.id
            return new_msg
        return False

    # pseudo static method of reading new lines from job and writing it to stdout
    @staticmethod
    def async_write_logs2stdout(tornado_worker, job, lines, log_level=logging.INFO):
        array = []
        for line in lines:
            if line != "":
                if line.startswith(core.core.command_delimiter):
                    # all command has a length  256 symbols
                    log_msg = tornado_worker.process_command(line, job)
                    if log_msg:
                        print(log_msg.message)
                        array.append(log_msg)
                    job.update()
                else:
                    if job.current_job:
                        log_msg = LogMessage(message=line,
                                             job=job.current_job.id,
                                             task_id=job.task_id,
                                             job_process=job,
                                             task_state=JobDataModel.STATUS_RUNNING,
                                             source="worker",
                                             level=log_level)
                        array.append(log_msg)
                    print(line)
        return array

    # pseudo static method of reading new lines from job
    @staticmethod
    def async_read_logs(tornado_worker, job, lines, log_level=logging.INFO):
        array = []
        for line in lines:
            if line != "":
                if line.startswith(core.core.command_delimiter):
                    # all command has a length  256 symbols
                    log_msg = tornado_worker.process_command(line, job)
                    if log_msg:
                        array.append(log_msg)
                    job.update()
                else:
                    job.update()
                    log_msg = tornado_worker.put_new_message(LogMessage(message=line,
                                                                        job_object=job.current_job,
                                                                        task_id=job.task_id,
                                                                        job_process=job,
                                                                        task_state=JobDataModel.STATUS_RUNNING,
                                                                        source="worker",
                                                                        level=log_level))
                    if log_msg:
                        array.append(log_msg)
        return array

    def process_command(self, line, job):
        command = line.split(core.core.command_delimiter)
        command_json = json_decode(command[1])
        if command_json["command"] == "start_work_job":
            job.setup_job(int(command_json["job_id"]))
            logging.debug("job is setuping %i" % command_json["job_id"])
            return False

        if command_json["command"] == "error":
            line = "<a id='error{0}' href='#'><strong>{1}</strong></a>\
                    <p class='error{0} error'>{2}</p>".format(command_json["job_id"],
                                                              command_json["message"],
                                                              command_json["trace"])
            log_msg = self.put_new_message(LogMessage(message=line,
                                                      job_object=job.current_job,
                                                      task_id=job.task_id,
                                                      job_process=job,
                                                      task_state=JobDataModel.STATUS_RUNNING,
                                                      source="worker",
                                                      level=logging.ERROR))

            return log_msg

        # means unrecognized command
        if command_json["command"] == "ping":
            return False
        return False

    @staticmethod
    def process_finished(self, job, exit_code, user_callback=None):

        # update state of job from database
        status = JobDataModel.STATUS_DONE
        if exit_code != 0 and exit_code != 13:
            status = JobDataModel.STATUS_FAILED
        logging.debug("job %s is  dead" % str(job.task_id))
        # clean the garbage
        # if everything ok, than get task and check if it was all
        message = None
        job.current_job.status = status
        job.current_job.save()
        job.update(status)
        if status == JobDataModel.STATUS_DONE:
            job.cleanup()
            message = LogMessage(message="task has been finished \n",
                                 job_object=job.current_job,
                                 job_process=job,
                                 task_id=job.task_id,
                                 task_state=status,
                                 level=logging.INFO,
                                 source="worker")

        else:

            task = TaskManager.get_task(job.task_id)
            # but if exit code != 1, cause exit code 1  means that worker has finished jobs by itself
            if exit_code != 1:
                task.update(status=JobDataModel.STATUS_FAILED)

            message = LogMessage(message="task has been failed \n",
                                 job_object=job.current_job,
                                 job_process=job,
                                 task_id=job.task_id,
                                 task_state=status,
                                 level=logging.INFO,
                                 source="worker")

        if user_callback:
            logging.debug("call the user callback %s" % str(job.task_id))
            user_callback(job, exit_code)
        else:
            self.put_new_message(message)

        # Special exit code for restarting process
        if exit_code == 13:
            sys.exit(exit_code)

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


    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        obj = json_decode(message)
        self.writing_logs(obj)
        return

    # write logs to socket
    def writing_logs(self, obj):
        # if requested task logs is not equal to current task than this task is pending
        if obj["msg"] == "hello":
            # connect task manager task_id and web socket task_id
            self.write_message(json_encode({"status": False, "data": {}}))
            return

        # process socket connection if depends
        task_id = int(obj["task_id"])
        if task_id in self.configs["buffer"]:
                messages = []
                now_time = time.time()
                # get dict repr for json
                desc = None
                state = None
                status = False
                for item in self.configs["buffer"][task_id]:
                    job_id = ""
                    if item.job_object:
                        job_id = item.job_object.id
                    messages.append({"created": now_time,
                                     "message": item.message,
                                     'level': item.level,
                                     'job_id': job_id })
                    status = True
                    if item.job_process is not None:
                        # main question
                        desc = item.job_process.dict_repr()
                        state = item.task_state

                self.configs["buffer"][task_id] = []

                if len(messages) > 0:
                    result = {"status": status,
                              "state": state,
                              "data": {"task": desc,
                                       "log_messages": messages}}

                    self.write_message(json_encode(result))
                else:
                    self.write_message(json_encode({"status": False}))
                return

        else:
            self.write_message(json_encode({"status": False,
                                            "state": "pending",
                                            "data": {}}))
            return

    # just write something, when we are closed
    def on_close(self):
        logging.debug("closed")

# i have leave it only in debugging way
class MainHandler(tornado.web.RequestHandler):

    def initialize(self, configs):
        self.configs = configs

    @tornado.web.asynchronous
    def get(self):
        self.write(Page)
        self.finish()


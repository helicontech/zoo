# -*- coding: utf-8 -*-
import subprocess
import sys
import os
from core.models.database import JobPeewee, TaskPeewee, PeeweeLogMessage
from core.task import Task
from core.task_manager import TaskManager
from datetime import datetime
import json
import logging
import collections
from core.helpers.common import json_decode
import core.core
import pyuv
import threading
import time

class JobAsyncCoreUpdate(threading.Thread):

    def __init__(self, core):
        self.core = core
        threading.Thread.__init__(self)

    def run(self):
        self.core.update(True)

class Job:

    _jobs = {}  # активные job-ы который запланированы в работу

    @classmethod
    def clean_job(cls, task_id):
        """
        удалить job-e -> True если нет - False
        :param job:
        :return:
        """
        if task_id in cls._jobs:
            del cls._jobs[task_id]
            return True
        return False

    @classmethod
    def get_job(cls, task_id):
        """
        получить job-e по task_id, если нет - None
        :param task_id:
        :return:
        """
        return cls._jobs.get(task_id, None)

    @classmethod
    def create_job(cls, task, core):
        """
        создать job-у на выполнение


        :param task:
        :param core:
        :return:
        """
        if not task.data_model.id in cls._jobs:
            job = Job(task, core)
            cls._jobs[task.data_model.id] = job

        return cls._jobs[task.data_model.id]

    """
        Manager working with task,
        get new tasks
        create job
    """
    def __init__(self, task, core):
        self.process = None
        self.log_manager = None

        if isinstance(task, Task):
            self.data_model = task.data_model
            self.task = task
        else:
            raise RuntimeError("task should be a Task object")
        self.status = JobPeewee.STATUS_PENDING
        self.id = None
        # alias for id
        self.task_id = self.data_model.id
        self.current_job = None
        self.last_log_chunk = ""
        self.updated = None
        self.core = core
        self.pipe_stdin = None
        self.pipe_stdout = None
        self.pipe_stderr = None
        self.direvents = None
        self.bulk_insert = []

    def __repr__(self):
        return ",".join(["task", str(self.data_model.id)])

    def task2json(self, parent_pid):
        task = TaskManager.get_task(self.task_id)
        JobList = []
        for job in task.jobs:
            dict_obj = {"job_id": job.id,
                        "params": json_decode(job.params),
                        "command": job.command,
                        "parent_pid": parent_pid}
            JobList.append(dict_obj)
        return json.dumps(JobList)

    def setup_job(self, job_id: int):
        # method that clean some garbage
        if self.current_job is not None:
            self.current_job.status = JobPeewee.STATUS_DONE
            self.current_job.save()

        self.current_job = JobPeewee.get(JobPeewee.id == job_id)
        self.current_job.status = JobPeewee.STATUS_RUNNING
        self.current_job.save()


    def update(self, status=None):
        # method that clean some garbage
        self.updated = datetime.now()
        if status is None:
            status = JobPeewee.STATUS_RUNNING
        self.data_model.status = status
        self.status = status

    def cleanup(self):
        logging.debug("cleanup up %i " % self.task_id)
        if self.status == JobPeewee.STATUS_DONE:
            self.log_manager.clean_all()
            self.log_manager.free()
        else:
            self.log_manager.free()

    @staticmethod
    def start_job(job, log_object, callback_exit, callbak_newlogs):
        log_object.setup_log(job.task_id)
        job.log_manager = log_object
        job.process = job.__start_process(callback_exit, callbak_newlogs)
        job.data_model.save()
        job.status = JobPeewee.STATUS_RUNNING
        job.updated = datetime.now()

    # start working on task
    def start_job_async(self, log_object, callback_exit, callbak_newlogs):
        callable_object = lambda: Job.start_job(self, log_object, callback_exit, callbak_newlogs)
        event_loop = core.core.core_event_loop
        setup_task = lambda errno: self.setup_task()
        event_loop.queue_work(callable_object, setup_task)
        return True



    def __start_process(self, callback_exit, callbak_newlogs):


        event_loop = core.core.core_event_loop
        stdio = []
        self.pipe_stdin = pyuv.Pipe(event_loop)
        self.pipe_stdout = pyuv.Pipe(event_loop)
        self.pipe_stderr = pyuv.Pipe(event_loop)
        # Создание пайпа для stdin. В pipewrite мы будем писать на нашем конце, а piperead передадим child-у
        (piperead, pipewrite) = os.pipe()
        self.pipe_stdin.open(pipewrite)
        # Можно записать в пайп что-то заранее, чтобы процесс сразу получил данные

        stdio.append(pyuv.StdIO(fd=piperead, flags=pyuv.UV_INHERIT_FD))
        stdio.append(pyuv.StdIO(self.pipe_stdout, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))
        stdio.append(pyuv.StdIO(self.pipe_stderr, flags=pyuv.UV_CREATE_PIPE|pyuv.UV_WRITABLE_PIPE))

        self.direvents = pyuv.fs.FSEvent(event_loop)

        fsevents_callbak = lambda fsevent_handle, filename, events, error: Job.fsevent_callback(self,
                                                                                                fsevent_handle,
                                                                                                filename, events,
                                                                                                error,
                                                                                                callbak_newlogs)
        self.direvents.start(self.log_manager.get_log_dir(), 0, fsevents_callbak)
        self.direvents.ref = False

        # it's needed for zoocmd.exe
        frozen = getattr(sys, 'frozen', False)
        logging.debug("start slave %s it's frozen %s " % (sys.executable, str(frozen)))
        args = None
        if frozen:
            args = ['-u', '--task-work={0}'.format(self.task_id),
                          '--task-log={0}'.format(self.log_manager.common_working_log())]
        else:
            args = ['-u', sys.argv[0], '--task-log={0}'.format(self.log_manager.common_working_log()),
                                       '--task-work={0}'.format(self.task_id)]

        job_callback_exit = lambda proc, exit_status, term_signal: Job.process_exit(self, exit_status, term_signal,
                                                                                    callback_exit)

        proc = pyuv.Process.spawn(event_loop, args=args,
                                  executable=sys.executable,
                                  exit_callback=job_callback_exit,
                                  stdio=stdio)

        self.pipe_stdout.start_read(lambda handle, data, error: Job.read_cb(self, handle, data,
                                                                            error, callbak_newlogs))
        self.pipe_stderr.start_read(lambda handle, data, error: Job.read_cb(self, handle, data,
                                                                            error, callbak_newlogs, logging.ERROR))

        # write a task json represantation

        return proc

    def setup_task(self):
        logging.debug("setup task through pipe")
        command = "%s%s%s\r\n" % (core.core.command_delimiter,
                                  self.task2json(os.getpid()),
                                  core.core.command_delimiter)
        logging.debug("send to client command %s" % command)

        self.pipe_stdin.write(command.encode("utf-8"))

    @staticmethod
    def save_log_msgs(bulk_insert: list):
        logging.debug("insert to the database")
        logging.debug(bulk_insert)
        for item in bulk_insert:
                item.save()

    @staticmethod
    def process_exit(job, exit_status, term_signal,  callback):
        # stop reading all pipes and close it
        try:
            # think where is it must be
            if Job.clean_job(job):
                logging.debug("normal deleting from inner dict")
            else:
                logging.debug("something wrong with  deleting from inner dict")

            callable_object = lambda: Job.save_log_msgs(job.bulk_insert)
            event_loop = core.core.core_event_loop
            event_loop.queue_work(callable_object)
            logging.debug("Process of worker is stoped %d and term signal %d" % (exit_status, term_signal))
            if not job.pipe_stdin.closed:
                logging.debug("close pipe  in %s" % (job.pipe_stdin))
                job.pipe_stdin.close()
            if not job.pipe_stdout.closed:
                logging.debug("close pipe out  %s" % (job.pipe_stdout))
                job.pipe_stdout.close()
            if not job.pipe_stderr.closed:
                logging.debug("close pipe err  %s" % (job.pipe_stderr))
                job.pipe_stderr.close()

            logging.debug("stop direvents   %s" % (job.direvents))
            job.direvents.stop()
            job.pipe_stdin = None
            job.pipe_stdout = None
            job.pipe_stderr = None
            job.direvents = None
            job.process = None
        except:
            logging.error("Error has been occured during the closing fs pipes")
        finally:
            # send api request to update install yaml
            async_core_update = JobAsyncCoreUpdate(job.core)
            async_core_update.run()
            callback(job, exit_status)

    @staticmethod
    def fsevent_callback(job, fsevent_handle, filename, events, error, callbak_newlogs):
        self = job
        if error is None:
            if events & pyuv.fs.UV_CHANGE:
                logging.debug('File changed:\n\r%s' % filename)
                self.log_manager.update_list_checking_files(filename)
                lines = self.log_manager.read_new()
                log_message = callbak_newlogs(lines, logging.INFO)
                if len(log_message)>0 :
                    job.bulk_insert += log_message
        else:
            logging.debug("some error has been occured %s: %s" % (error, pyuv.errno.strerror(error)))

    @staticmethod
    def read_cb(job, handle, data, error, callbak_newlogs, log_level=logging.INFO):
        if data is None:
            return

        self = job
        self.updated = datetime.now()
        if error is not None:
            logging.info('Pipe read  %s' % data)
            logging.error('Pipe read error %s: %s' % (error, pyuv.errno.strerror(error)))
        logging.debug("%i Received data: %s" % (job.task_id, data))
        if data is not None:
            line = data.decode(encoding='utf-8', errors='ignore')
            array = line.splitlines()
            array[0] = self.last_log_chunk + array[0]
            lines_to_client = None
            if not line.endswith("\n"):
                job.last_log_chunk = array[-1:][0]
                lines_to_client = array[:-1]
            else:
                job.last_log_chunk = ""
                lines_to_client = array

            logging.debug(" send to client : %s" % lines_to_client)
            log_message = callbak_newlogs(lines_to_client, log_level)
            if len(log_message) > 0:
                job.bulk_insert += log_message

    # dict description for session is needed by
    def dict_repr(self):
            representation = dict()
            representation["status"] = self.data_model.status
            representation['created'] = self.data_model.created.isoformat()
            representation['updated'] = self.updated.isoformat()
            representation['settings'] = self.data_model.settings
            if self.data_model.status in (JobPeewee.STATUS_DONE, JobPeewee.STATUS_FAILED):
                representation['is_finished'] = True
            else:
                representation['is_finished'] = False

            return representation

    # deprecated
    def set_products_installed(self, core):
        self.reload()

        # HACK

        from .models.application import Application
        from .models.engine import Engine
        from .models.product import Product


        product = self.state["products"][0]
        product2Install = product
        if "application" in product:
            product2Install = Application(core, product)
        if "engine" in product:
            product2Install = Engine(core, product)
        if "product" in product:
            product2Install = Product(core, product)

        if self.data_model.command == "uninstall":
            core.set_product_uninstalled(product2Install)
        else:
            parameters = self.state["parameters"]
            product2Install.merge(**product)
            core.set_product_installed(product2Install, parameters)

    # make task fail
    def job2fail(self):
        try:
            self.data_model.status = JobPeewee.STATUS_FAILED
            self.data_model.save()
            return True
        except BaseException:
            return False

    # make task canceled
    def job2canceled(self):
       # try:
            logging.debug("cancel job %i" % self.data_model.id)
            self.task.update(JobPeewee.STATUS_CANCELED)
            return True
        #except BaseException:
         #   return False

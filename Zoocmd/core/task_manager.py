# -*- coding: utf-8 -*-
from core.models.database import JobPeewee as JobDataModel
from core.models.database import TaskPeewee as TaskDataModel
from core.task import Task
from datetime import datetime
from core.core import Core
from core.exception import SelfUpgradeException
import urllib
from core.log_message import LogMessage
import json
from core.product_collection import ProductCollection
from core.parameters_manager import ParametersManager
from core.helpers.common import json_encode, json_decode
import core.version
import logging

class TaskFactory(object):

    @staticmethod
    def execute_job(params: dict):
        """
        выполнить это задание, в этом процеесе
        выбрать параметре
        выбрать метод
        вывать у ядра нужный метод с параметрами
        ждать пока доделает

        это длинный и блокирующий метод, должен вызываться или из консоли, или из воркера
        никонгда из UI

        :raise ValueError:
        """

        if params["command"] == JobDataModel.COMMAND_INSTALL:
            logging.debug("ok everything good i'm going to install")

            return TaskFactory.command_install(params)

        elif params["command"] == JobDataModel.COMMAND_UPGRADE:
            return TaskFactory.command_upgrade(params)

        elif params["command"] == JobDataModel.COMMAND_UNINSTALL:
            return TaskFactory.command_uninstall(params)

        else:
            raise ValueError('Invalid task command: {0}'.format(params["command"]))

    @staticmethod
    def command_install(params):
        state = params["params"]
        return Core.get_instance().install(state['products'], state['parameters'],
                                                      False, True)


    @staticmethod
    def command_upgrade(params):
        state = params["params"]
        # check self upgrading
        if "product" in state["products"][0] and state["products"][0]["product"] == core.version.NAME:

            Core.get_instance().upgrade(state['products'], state.get('parameters'), True)
            raise SelfUpgradeException("Helicon Zoo is upgrading yourself", params["parent_pid"])
        else:
            return Core.get_instance().upgrade(state['products'], state.get('parameters'), True)



    @staticmethod
    def command_uninstall(params):
        state = params["params"]
        return Core.get_instance().uninstall(state['products'], state.get('parameters'))

    @staticmethod
    def create_task(type_task, products: ProductCollection, parameter_manager: ParametersManager=None):
        if type_task == "install":
            return TaskFactory.create_install_task(products, parameter_manager)
        if type_task == "uninstall":
            return TaskFactory.create_uninstall_task(products)
        if type_task == "upgrade":
            return TaskFactory.create_upgrade_task(products, parameter_manager)

        return None





    @staticmethod
    def create_install_task(products: ProductCollection,
                            parameter_manager: ParametersManager):
        """
        фабричный метод: создать такс с переданными параметрами, с типом COMMAND_INSTALL
        сохранить в базе данных
        зхапустить воркер
        :param products:  продукты для установки (продукты которые выбрал пользователь + зависимости)
        :param parameter_manager:
        :return: номер таска
        """
        settings = json_encode(Core.get_instance().settings.get_state())
        job_array = []
        task_object = TaskDataModel(command="install", settings=settings)
        for product in products:
            title = product.title

            state = {
                'products': [product.to_dict()],
                'parameters': parameter_manager.get_state()
            }
            state2save = json_encode(state)

            job = JobDataModel(
                command=JobDataModel.COMMAND_INSTALL,
                title=title,
                params=state2save,
                task=task_object,
                settings=settings
            )
            job_array.append(job)
        task = Task(task_model=task_object, jobs=job_array)
        return task

    @staticmethod
    def create_upgrade_task(products: ProductCollection, parameter_manager: ParametersManager):
        """
        фабричный метод: создать такс с переданными параметрами, с типом COMMAND_UPGRADE
        сохранить в базе данных
        зхапустить воркер

        :param products:
        :param parameter_manager:
        :return:
        """
        settings = json_encode(Core.get_instance().settings.get_state())
        job_array = []
        task_object = TaskDataModel(command="upgrade", settings=settings)
        for product in products:
            title = product.title

            state = {
                'products': [product.to_dict()],
                'parameters': parameter_manager.get_state()
            }
            state2save = json_encode(state)

            job = JobDataModel(
                command=JobDataModel.COMMAND_UPGRADE,
                title=title,
                params=state2save,
                task=task_object,
                settings=settings
            )
            job_array.append(job)
        task = Task(task_model=task_object, jobs=job_array)
        return task

    @staticmethod
    def create_uninstall_task(products: ProductCollection):
        """
        фабричный метод: создать такс с переданными параметрами, с типом COMMAND_UNINSTALL
        сохранить в базе данных
        зхапустить воркер

        :param requested_products:
        :param products:
        :param parameter_manager:
        :return:
        """

        job_array = []
        settings = json_encode(Core.get_instance().settings.get_state())

        task_object = TaskDataModel(command="uninstall", settings=settings)
        for product in products:
            state = {
                'products': [product.name],
            }
            job = JobDataModel(
                command=JobDataModel.COMMAND_UNINSTALL,
                title=product.title,
                params=json_encode(state),
                settings=settings)
            job_array.append(job)

        task = Task(task_model=task_object, jobs=job_array)
        return task



class TaskManager:
    """
        Manager working with tasks,
        get new tasks
        create job

    """
    def __init__(self, core):
        self.core = core
        self.configs = {}
        self.job = None
        self.task_id = None

    # method from from old version
    @staticmethod
    def rerun_task(task):
        """
        повтонрно выполнить задание N
        удобно для оталадки,
        удобно если что-то упало, повторить снова
        :param task:
        :return:
        """
        task.status = JobDataModel.STATUS_PENDING
        # todo remove it
        task.logmessage_set.all().delete()
        task.error_message = ''
        task.save()
        return task.id

    # find running job
    # deprecated
    @staticmethod
    def get_running_job():

        ret = Core.get_lock(JobDataModel.LOCK)
        if not ret:
            return None
        else:
            job_id = int(ret)
            try:
                job = JobDataModel.get(JobDataModel.id == job_id)
                return job
            except JobDataModel.DoesNotExist:
                return None

    # save task to queue table
    # deprecated
    @staticmethod
    def queue_task(task: Task):
        task.data_model.save()
        for i in task.jobs:
            i.task = task.data_model
            i.save()
        task.id = task.data_model.id
        return task.data_model.id


    # get object task from database
    @staticmethod
    def get_task(task_id: int):
        """
        get task from database by task_id

        :param task_id:
        :return: Task
        """

        global_task = JobDataModel.select().where(JobDataModel.task == task_id,
                                                  JobDataModel.status == JobDataModel.STATUS_PENDING)
        atom_jobs = []
        for i in global_task:
            atom_jobs.append(i)

        try:
            task_object = TaskDataModel.get(TaskDataModel.id == task_id)
            task = Task(task_model=task_object, jobs=atom_jobs)
            return task
        except TaskDataModel.DoesNotExist:
            return None

    # may be we need use Job class instead of this method
    # check if task is alive
    @staticmethod
    def is_job_alive(core, job_id):

        try:
            obj = JobDataModel.get(JobDataModel.id == job_id)
            # may be wrong
            logging.debug("find possible alive task %i pid is %i %s" % (job_id, obj.pid, obj.status))

            if obj.status == JobDataModel.STATUS_EXCEPTION:
                return False
            if obj.status == JobDataModel.STATUS_FAILED:
                return False
            if obj.status == JobDataModel.STATUS_DONE:
                return False

            pid = obj.pid

            return core.api.os.shell.is_alive(pid)
        except JobDataModel.DoesNotExist:
            return False






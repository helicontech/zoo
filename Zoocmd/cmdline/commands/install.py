# -*- coding: utf-8 -*-

from core.core import Core
from core.parameters_parser import ParametersParserStr, ParametersParserJsonFile, ParametersParserYmlFile
from core.dependency_manager import DependencyManager
from argparse import ArgumentParser
import core.core
import logging
from core.product_collection import ProductCollection
from core.dependency_manager import DependencyManager
from core.parameters_manager import ParametersManager
from core.parameters_parser import ParametersParserJson
from core.parameters_parser import  EmptyParameters
from core.task_manager import TaskManager, TaskFactory
from web.taskqueue.tornado_worker import TornadoWorker
import web
import sys

class InstallCommandError(Exception):
    pass


class InstallCommand(object):
    """
    install command wrapper class
    """

    def __init__(self, product_names: list, args_parameters: ArgumentParser):
        """
        initialize install wrapper
        :param product_names: list or products names
        :param args_parameters: dict of install parameters
        """
        if not product_names:
            raise InstallCommandError('no products specified')

        self.core = core.core.Core.get_instance()
        self.product_names = product_names
        self.args_parameters = args_parameters

    def do(self):
        """
        Install products by tornado  worker
        """

        parameters = None
        dm = DependencyManager()
        product_flat_list = [dm.get_dependencies(product_name) for product_name in self.product_names]
        product_list = InstallCommand.flat_deps4products(product_flat_list, False)

        if self.args_parameters.yml_params:

            parameters = ParametersParserYmlFile(self.args_parameters.yml_params).get()

        elif self.args_parameters.json_params:

            parameters = ParametersParserJsonFile(self.args_parameters.json_params).get()

        elif self.args_parameters.parameters:

            parameters = ParametersParserStr(self.args_parameters.parameters).get()

        else:
            # then fill with empty params
            parameters = EmptyParameters().get(product_list)

        # добывает список продуктов из списка имён
        products = ProductCollection(product_list, feeds=(self.core.feed, self.core.current), ready_json=True)
        # парсим параметры установки из запроса
        # создаём менеджер параметров
        parameter_manager = ParametersManager(self.core, products, parameters)
        # все ли параметры заполнены?
        if parameter_manager.are_all_parameters_filled():

            # TODO move TornadoWorker to core
            # create tornado worker
            web.taskqueue.tornado_worker.TornadoWorker.create_instance()

            # всё ок, создаём задание на установку
            task = TaskFactory.create_task("install", products, parameter_manager)
            task_id = TaskManager.queue_task(task)
            callback_exit = lambda job, exit_code: InstallCommand.console_exit(self, job, exit_code)
            TornadoWorker.start_new_task(task, callback_exit, False)
            core.core.core_event_loop_start()
        else:
            raise InstallCommandError("Not all parameters specified")

    @staticmethod
    def console_exit(self_object, job, exit_code):
        core.core.core_event_loop_stop()
        if exit_code != 0:
            logging.info("The task has finished unsuccessfully")
            sys.exit(1)

    @staticmethod
    def flat_deps4products(product_list, installed=True):
        result_list = []
        for product in product_list:
            if "and" in product:
                inner_list = InstallCommand.flat_deps4products(product["and"], installed)
                result_list += inner_list

            # we can process only one level of  "or" list
            if "or" in product:
                # for product_item in product:
                result_list.append(InstallCommand.flat_deps4products(product["or"], installed))

            # installed version is not existed
            if "product" in product and product["product"]["installed_version"] == '':
                if not installed:
                    result_list.append(product["product"])
                    continue

            # installed version is existed
            if "product" in product and product["product"]["installed_version"] != '':
                if installed:
                    result_list.append(product["product"])
                    continue

        return result_list




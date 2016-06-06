# -*- coding: utf-8 -*-
import logging
from core.core import Core
import core.core
from core.parameters_parser import ParametersParserStr
from core.product_collection import ProductCollection
from core.dependency_manager import DependencyManager
from core.parameters_manager import ParametersManager
from core.parameters_parser import ParametersParserJson
from core.parameters_parser import  EmptyParameters
from core.task_manager import TaskManager, TaskFactory
from web.taskqueue.tornado_worker import TornadoWorker
import sys


class UninstallCommandError(Exception):
    pass


class UninstallCommand(object):
    """
    Helper class to uninstall products from cmd line
    """
    def __init__(self, product_names, args_parameters=None):
        if not product_names:
            raise UninstallCommandError('no products specified')

        self.core = Core.get_instance()
        self.product_names = product_names
        self.args_parameters = args_parameters

    def do(self):
        """
        Do uninstall
        """
        products = ProductCollection([product_name for product_name in self.product_names],
                                     feed=Core.get_instance().current_storage.feed,
                                     fail_on_product_not_found=False)
        TornadoWorker.create_instance()
        # всё ок, создаём задание на установку
        task = TaskFactory.create_task("uninstall", products, EmptyParameters())
        task_id = TaskManager.queue_task(task)
        callback_exit = lambda job, exit_code: UninstallCommand.console_exit(self, job, exit_code)
        TornadoWorker.start_new_task(task, callback_exit, False)
        core.core.core_event_loop_start()
        sys.exit(0)

    @staticmethod
    def console_exit(self, job, exit_code):
        core.core.core_event_loop_stop()
        if exit_code != 0:
            logging.info("The task has finished unsuccessfully")
            sys.exit(1)

    @staticmethod
    def flat_deps4products(product_list, installed=True):
        result_list = []
        for product in product_list:
            if "and" in product:
                inner_list = UninstallCommand.flat_deps4products(product["and"], installed)
                result_list += inner_list

            # we can process only one level of  "or" list
            if "or" in product:
                # for product_item in product:
                result_list.append(UninstallCommand.flat_deps4products(product["or"], installed))

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

        return  result_list
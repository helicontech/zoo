# -*- coding: utf-8 -*-

import sys


from core.core_loader import CoreLoader
from core.helpers.log_format import format_dict
from core.helpers.common import str_list_to_dict
from core.start import setup_logs
import os

from .commands.uninstall import UninstallCommand
from .commands.test import RunTestCommand
from .commands.sync import SyncCommand
from .commands.list import ListProductsCommand
from .commands.install import InstallCommand
from .commands.runserver import RunServerCommand
from .commands.run_install_worker import  RunTaskWorkerCommand

import logging
from core.settings import Settings
import core.core
from core.interlocks import InterProcessLock, SingleInstanceError
import time


"""
Маршрутизатор команд из аргументов коммандной строки
"""


def process_commands(args, settings: Settings):
    """
    Start Core and route cmd line commands
    :param args: parsed cmd line argumens (parser.parse_args())
    :param settings: Core will be created with this settings, by default they are loaded from settings.yaml
    :return: None
    """

    # if quiet mode - redefine stdout and stderr
    if args.quiet:
        sys.stdout = open("NUL", 'w')
        sys.stderr = open("NUL", 'w')


    # get debug level
    log_level_str = args.log_level or os.environ.get('LOG_LEVEL') or 'INFO'
    log_level_str = log_level_str.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    # #

    if args.zoo_compile:
        from .commands.zoo_compile import make_build
        make_build(args.zoo_compile)
        return

    core_loader = CoreLoader.get_instance()
    # start loader, core will be created and initialized in thread

    # process commands that do not require the core
    if args.run_server:

        setup_logs(settings.logs_path, log_level, settings.logs_conf)
        # commands that require the core, wait core creation
        logging.info("zoo is starting")
        logging.info(" ".join(sys.argv))
        core_loader.start(settings, make_sync=True)
        cmd = RunServerCommand(settings, args.run_server_addr)
        logging.info("web server is going to run")
        cmd.run()

        return

    if args.run_test:

        setup_logs(settings.logs_path, log_level, settings.logs_conf)
        # commands that require the core, wait core creation
        logging.info("starting test zoo")
        core_loader.start(settings, make_sync=True)
        core = core_loader.wait_core()
        cmd = RunTestCommand(core)
        logging.info("functional tests are going to run")
        cmd.run()

        return



    # print settings
    if args.get_settings:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        settings = core.settings.get_state()
        print(format_dict(settings))
        return

    # set settings from cmd
    if args.set_settings:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        core.set_settings(str_list_to_dict(args.set_settings))
        settings = core.settings.get_state()
        print(format_dict(settings))
        return

    # subprocess of installing
    if args.task_id:
        task_lock = InterProcessLock(name="zoo_task_worker")

        # infinite cycle of trying locking
        try:
            task_lock.lock()
        except SingleInstanceError:
            print("Another installation is currently running. Your installation should begin shortly.")
            while True:
                time.sleep(1)
                try:
                    task_lock.lock()
                    break
                except SingleInstanceError:
                    pass

        # configure logger for task works
        logger = logging.getLogger()
        # remove all handlers
        logger.handlers = []
        logger.setLevel(logging.DEBUG)

        filename = os.path.join(settings.logs_path, args.task_log)
        logging.Formatter('%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s')
        ch = None
        if args.task_log:
            ch = logging.FileHandler(filename, mode='a')

        ch1 = logging.StreamHandler(sys.stdout)
        ch1.setLevel(logging.INFO)
        logger.addHandler(ch)
        logger.addHandler(ch1)
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        core.log_manager.setup_log(int(args.task_id))
        logging.info('Instantiating installation worker with following settings:\n{0}'.format(core.settings.format()))
        RunTaskWorkerCommand(core, args.task_id).run()
        task_lock.unlock()
        # delete log
        return

    # print products
    if args.list_products:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        ListProductsCommand(core.feed).products()
        return

    # print installed products
    if args.show_installed:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        ListProductsCommand(core.feed).installed()
        return

    # search products and print
    if args.search:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        ListProductsCommand(core.feed).search(args.search)
        return

    # search installed products
    if args.sync:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        SyncCommand(core).do()
        return

    logger = logging.getLogger()
    # remove all handlers
    logger.handlers = []
    filename = "%s/_zoo_server.log" % settings.logs_path
    ch1 = logging.StreamHandler(sys.stdout) # logging.FileHandler(filename, mode='a')
    ch = logging.StreamHandler(sys.stdout)
    logging.Formatter('%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s')
    ch1.setLevel(logging.DEBUG)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch1)
    logger.addHandler(ch)
    logger.setLevel(log_level)

    # install products from cmd line
    if args.install:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        # set interactive mode
        core.interactive = args.interactive
        InstallCommand(args.products, args).do()
        return

    # uninstall products from cmd line
    if args.uninstall:
        core_loader.start(settings)
        # commands that require the core, wait core creation
        core = core_loader.wait_core()
        # set interactive mode
        core.interactive = args.interactive
        UninstallCommand(args.products, args.parameters).do()
        return


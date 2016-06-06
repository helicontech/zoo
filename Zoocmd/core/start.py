# -*- coding: utf-8 -*-

import logging
import os
import logging.config

def start(settings):
    """
    Стартует ядро. Вызывается из CoreLoader или юнит-тестов.
    :param settings: настройки, с которыми создавать ядро.
    """
    from .core import Core
    if Core.is_created():
        return Core.get_instance()
    core = Core.create_instance(settings=settings)
    return core

def setup_logs(log_dir, log_level = logging.INFO, conf=None):
    # set up addition log file when server starts from ui.exe
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger()
    log_path = os.path.join(log_dir, '_zoo_server.log')

    logger.setLevel(log_level)
    if conf is not None:
        try:
            logging.config.fileConfig(conf, defaults={'logfilename': log_path})
        except:
            default_logging(logger, log_path)
    else:
        default_logging(logger, log_path)

def default_logging(logger, log_path):
    ch = logging.handlers.RotatingFileHandler(log_path, mode='a', maxBytes=5000000, backupCount=5)
    ch.setFormatter(logging.Formatter('F1 %(asctime)s %(levelname)s %(message)s '))
    logger.addHandler(ch)


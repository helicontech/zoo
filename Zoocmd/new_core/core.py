"""
Copyright © Helicon Tech. All rights reserved.
"""


import logging
import os
import os.path

from core.models.installed_product import InstalledProductInfo
from .log_manager import LogManager
from .error_manager import ErrorManager

import math
import json
import datetime
import peewee
import new_core.feed_manager
import new_core.settings_manager

"""
Переменные модуля
"""

settings = settings_manager.load_settings()
feeds = {}


"""
Вспомогательные функции
"""

def load_system_feeds(settings=None):
    pass


def save_system_feeds(settings=None):
    pass


def load_main_feeds(settings=None):
    pass


def assert_path_exist(path):
    """
    Создаёт диреткорию, если её ещё нет.
    """
    os.makedirs(path, exist_ok=True)


def init_core(settings_=None):
    nonlocal settings
    if settings_:
        settings = settings_

    # создадим папки, если еще не
    assert_path_exist(settings.storage_path)
    assert_path_exist(settings.cache_path)
    assert_path_exist(settings.logs_path)





"""
Основные функции
"""

def sync():
    """
    Trying to find all products installed. Generates 'current' feed
    :return:
    """
    pass


def get_products(feed=None):
    """
    Высокоуровневая функция, возвращает список всех продуктов в Zoo. Можно указать конкретный фид.
    По умолчанию все продукты в Zoo, с заполненными данными о установленных версиях и т.п.
    :param feed:
    :return:
    """
    pass


def get_engines(feed=None):
    """
    Высокоуровневая функция, возвращает список всех Engines в Zoo. Можно указать конкретный фид.
    По умолчанию все Engines в Zoo, с заполненными данными о установленных версиях и т.п.
    :param feed:
    :return:
    """
    pass


def get_applications(feed=None):
    """
    Высокоуровневая функция, возвращает список всех Applications в Zoo. Можно указать конкретный фид.
    По умолчанию все Applications в Zoo
    :param feed:
    :return:
    """
    pass

def get_product_names(feed=None):
    """

    :param feed:
    :return: Set of product names in feed
    """
    pass


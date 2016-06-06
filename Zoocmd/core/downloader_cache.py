# -*- coding: utf-8 -*-

import os
import os.path
import urllib.parse

from .core import Core


class DownloaderCache(object):
    """
    Помощник для работы с кешем, в котором лежат скачанные файлы продуктов.
    Для каждого продукта создаётся свой объект этого класса.
    """

    def __init__(self, product):
        self.core = Core.get_instance()
        self.product = product
        # директория где лежат файлы для этого продукта этой версии
        self.product_cache_path = DownloaderCache.get_cache_path_for_product(self.core.settings.cache_path, product)

    def assert_dirs(self):
        """
        Создаёт директорию кеша, если ее еще нет.
        """
        os.makedirs(self.product_cache_path, exist_ok=True)

    def get_path(self, filename):
        """
        Возвращает путь к файлу внутри кеша.
        :param filename: имя файла
        """
        return os.path.join(self.product_cache_path, filename)

    def is_in_cache(self, filename)-> bool:
        """
        Есть ли в файл в кеше?
        """
        path = self.get_path(filename)
        return os.path.exists(path) and os.path.isfile(path) and os.path.getsize(path) > 0

    def get_filename_from_url(self, url):
        """
        Возвращает имя файла из урла.
        """
        file_name = os.path.basename(urllib.parse.urlsplit(url).path)
        return self.core.envs.expandvars(file_name)

    @classmethod
    def get_cache_path_for_product(cls, cache_path, product):
        """
        Генерирует и возвращает путь директории в кеше для продукта.
        формат такой: <папка кеша>\<имя продукта>\<версия продукта>
        """
        return os.path.join(cache_path, product.name, product.version)

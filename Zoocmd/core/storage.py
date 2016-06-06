# -*- coding: utf-8 -*-

import os
import os.path
import logging

from .helpers.yaml_helper import YamlHelper
from .models.application import Application
from .models.base_product import BaseProduct
from .feed import Feed


class Storage(object):
    """
    Хранилище для фида
    умеет загружать фид из файла в память
    умеет сохранять фид из памяти в файл

    """

    def __init__(self, core, path):
        """
        Загружает фид, по указанному пути

        :param core:
        :param path:
        """
        self.core = core
        self.path = path
        self.feed = Feed(self.core, self.core.platform)
        self.assert_file_exists()
        self.feed.load(self.path)

    def __repr__(self):
        return 'Storage({0})'.format(self.path)

    def save(self):
        """
        сохранить фид в файл

        """
        self.assert_file_exists()
        YamlHelper.save(self.feed.get_products(), self.path)

    def update(self):
        """
        обновить фид из файла

        """
        if self.is_exists():
            self.feed.update()

    def set_product_installed(self, product: BaseProduct, parameters=None):
        """
        пометить продукт как установленный, сохранить фид

        :param product:
        :param parameters:
        :return:
        """
        logging.debug(product)
        if isinstance(product, Application):
            return

        if parameters:
            product.parameters = parameters

        self.feed.remove_product(product.name)
        self.feed.raw_collection.append(product.to_dict())
        self.save()

    def set_product_uninstalled(self, product: BaseProduct):
        """
        пометить продукт как не установленный, сохранить фид

        :param product:
        :return:
        """
        logging.debug(product)
        if isinstance(product, Application):
            return

        self.feed.remove_product(product.name)
        self.save()

    def get_installed_version(self, product: BaseProduct):
        """
        из фида найти для указанного продукта, его установелнную версию

        :param product:
        :return:
        """
        product = self.feed.get_product(product.name)
        if product:
            return product.version
        return None

    def get_product(self, product_name_version):
        """
        найти в этом фиде продукт по имени, можно указывать верисю

        :param product_name_version:
        :return:
        """
        product = self.feed.get_product(product_name_version)
        if not product:
            #logging.debug('product {0} not found in storage'.format(product_name_version))
            pass
        return product

    def is_product_installed(self, product_name_version):
        """
        проверить установлена ли указаная версия продукта?

        :param product_name_version:
        :return:
        """
        return self.get_product(product_name_version) is not None

    def assert_file_exists(self):
        """
        если путь не указан, то создать все диретории по этому путии сам файл
        """
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            open(self.path, 'a').close()

    def is_exists(self):
        """
        проверить есть ли такой путь

        :return:
        """
        return os.path.exists(self.path)

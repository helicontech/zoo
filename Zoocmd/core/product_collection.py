# -*- coding: utf-8 -*-

import logging

from core.helpers.log_format import format_dict
from core.models.base_product import BaseProduct


class ProductCollection(object):
    """
    Коллекция продуктов (простой список) в объектном виде.
    умеет добавлять продукты по имени из указанного фида
    """

    def __init__(self, product_names: list=None,  feed=None, feeds=None, ready_json=False, fail_on_product_not_found=True ):
        """
        :type feed: Feed
        :param product_names: string list of product names
        :param feed: core.storage.feed for installed products (uninstall process),
                       core.feed for all products
        """
        from core.core import Core

        self.core = Core.get_instance()
        self.feeds = []
        if feed:
            self.feeds.append(feed)
        if feeds:
            self.feeds.extend(feeds)
        if len(self.feeds) == 0:
            self.feeds.append(self.core.feed)
        self.fail_on_product_not_found = fail_on_product_not_found
        self.coll = []

        if ready_json:
            for dict_product in product_names:
                self.add_product_from_json(dict_product)
        else:
            if product_names :
                for name in product_names:
                    self.add_by_name(name)

    def __repr__(self):
        return "ProductCollection([{0}])".format(','.join([repr(p) for p in self.coll]))

    def __iter__(self):
        """
        реализация интерфейса, чтобы быть коллекцией

        :return:
        """
        return self.coll.__iter__()

    def __len__(self):
        """
        реализация интерфейса, чтобы быть коллекцией

        :return:
        """
        return self.coll.__len__()

    def __getitem__(self, item):
        """
        реализация интерфейса, чтобы быть коллекцией

        :param item:
        :return:
        """
        return self.coll[item]

    def add_product_from_json(self, product: dict):
        from .models.application import Application
        from .models.engine import Engine
        from .models.product import Product
        if "application" in product:
            product_obj = Application(self.core, product)
        if "engine" in product:
            product_obj = Engine(self.core, product)
        if "product" in product:
            product_obj = Product(self.core, product)


        product_obj.merge(**product)
        self.coll.append(product_obj)

    def append(self, product: BaseProduct):
        self.coll.append(product)

    def add_product(self, product: BaseProduct):
        """
        добавить продукт в коллекцию, проверить что валидный, что еще нету в этой коллекции
        :param product:
        :return: :raise Exception:
        """
        if product is None:
            if self.fail_on_product_not_found:
                raise Exception('No product to add')
            else:
                return

        if not (isinstance(product, BaseProduct)):
            raise Exception("is not BaseProduct - '{0}'".format(product))

        if self.product_in_coll(product):
            logging.debug("{0} already in the collection".format(product))
            return

        self.coll.append(product)

        # logging.debug("{0} have been added to collection".format(product))

    def add_by_name(self, product_name):
        """
        найти продукт по имени в фиде, добавить в коллекцию
        :param product_name:
        :raise Exception:
        """
        product = None
        for feed in self.feeds:
            product = feed.get_product(product_name)
            if product:
                break

        if product:
            self.add_product(product)
        else:
            if self.fail_on_product_not_found:
                raise Exception('Could not get product for {0} from feed'.format(product_name))

    def get_state(self):
        """
        Для апгрейда используется список продуктов с точной версией

        :return:
        """
        return [product.to_dict(True) for product in self.coll]

    def to_json_list(self):
        """
        Make json  serilizeable List
        :return:
        """

        return [product.to_dict() for product in self.coll]


    def to_dict(self):
        """
        Для сериализации в json

        :return:
        """
        return [product.get_product_with_version() for product in self.coll]

    def get_names_list(self):
        """
        Получить список имен продуктов, без версий

        :return:
        """
        return [product.name for product in self.coll]

    def get_names_list_with_version(self):
        """
        Получить список имен продуктов, с версиями

        :return:
        """
        return [product.get_product_with_version() for product in self.coll]

    def reverse(self):
        """
        Отсортировать коллекцию в обратном порядке

        :return:
        """
        return self.coll.reverse()

    def product_in_coll(self, product: BaseProduct):
        """
        Проверить есть ли уже такой продукт в этой коллекции
        :param product:
        :return:
        """
        for p in self.coll:
            if product.name == p.name:
                return True
        return False

    def pformat(self):
        """
        Распечатать в удобочитаемом виде

        :return:
        """
        return format_dict(self.to_dict())
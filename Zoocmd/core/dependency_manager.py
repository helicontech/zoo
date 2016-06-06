# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict

from core.exception import DependencyException
from core.core import Core
from core.models.engine import Engine
from core.parameters_manager import ParametersManager
from core.models.base_product import BaseProduct
from core.models.application import Application

from core.product_collection import ProductCollection


class DependencyManager(object):
    """
    Реализует сложную логику поиска зависимостей для продукта,
    списков продуктов
    с and, or  версиями и реревьями зависимостей
    """

    def __init__(self):
        from core.core import Core
        self.core = Core.get_instance()

    def __repr__(self):
        return 'DependencyManager()'

    def _get_dependencies_for_node(self, dep):
        """
        найти зависости для узла,
        это может быть
        - список or
        - список and
        - список продуктов, это как бы and
        - конкретный продукт


        ! рекурсивная магия !

        на выходе - дерево


        :param dep:
        :return: :raise Exception:
        """
        if isinstance(dep, OrderedDict) and len(dep) == 1:
            if dep.get("or"):
                result = dict()
                result["or"] = self._get_dependencies_for_node(dep.get("or"))
                return result

        if isinstance(dep, OrderedDict) and len(dep) == 1:
            if dep.get("and"):
                result = dict()
                result["and"] = self._get_dependencies_for_node(dep.get("and"))
                return result

        if isinstance(dep, list):
            result = list()
            for i in dep:
                result.append(self._get_dependencies_for_node(i))
            return result

        if isinstance(dep, str):
            # найти зависимости для конкретного продукта
            return self.get_dependencies(dep)

        raise Exception("Unexpected type: '{0}'".format(dep))

    def get_dependencies(self, product_name):
        """
        найти зависомости для продукта

        :param product_name:
        :return: :raise Exception:
        """
        if not isinstance(product_name, str):
            raise Exception("Expected string. got '{0}'".format(product_name))

        product = Core.get_instance().feed.get_product(product_name)
        result = dict()
        if product is None:
            raise DependencyException("We cant't find the product '{0}'".format(product_name), product_name)

        result["product"] = product.to_dict(True)

        parameter_manager = ParametersManager(self.core, [product])
        result['parameters'] = [product_parameter.to_dict() for product_parameter in parameter_manager.get_for_product(product)]
        if product.is_installed():
            result['can_upgrade'] = bool(product.upgrade_command)
            result['last_version'] = product.version == product.get_installed_version()
        else:
            result['can_upgrade'] = True
            result['last_version'] = False

        dependencies = product.get_dependencies()
        if isinstance(product, Application):
            # if application we generate dependency from spec params
            engines = []
            databases = []
            dependencies = []
            for i in product.engines:
                engines.append(i['engine'])

            if product.database_type is not None:
                for i in product.database_type:
                    databases.append(i)
                databases_deps = databases[0]
                if len(databases)>1:
                    databases_deps = OrderedDict()
                    databases_deps["or"] = databases

                dependencies.append(databases_deps)

            engines_deps = engines[0]
            if len(engines)>1:
                engines_deps = OrderedDict()
                engines_deps["or"] = engines

            dependencies.append(engines_deps)


        if dependencies is None or len(dependencies) == 0:
            return result

        result["and"] = self._get_dependencies_for_node(dependencies)

        return result


    def _check_requires_exist_or_add(self, dep, must_exist):
        if isinstance(dep, OrderedDict) and len(dep) == 1:
            if dep.get("or"):
                return  self._check_requires_exist_or_add(dep.get("or"), must_exist)

        if isinstance(dep, OrderedDict) and len(dep) == 1:
            if dep.get("and"):
                result = dict()
                return self._check_requires_exist_or_add(dep.get("and"), must_exist)

        if isinstance(dep, list):
            result = list()
            for i in dep:
                if isinstance(i, str):
                    if i in must_exist:
                        del must_exist[i]
                else:
                    must_exist = self._check_requires_exist_or_add(dep.get("and"), must_exist)
            return must_exist

        if isinstance(dep, str):
            # найти зависимости для конкретного продукта
            if dep in must_exist:
                del must_exist[dep]
            return must_exist

        raise Exception("Unexpected type: '{0}'".format(dep))




    def get_products_with_dependencies(self, product_collection: ProductCollection):
        """
        плоский список продуктов и их зависимостей
        :param product_collection:
        :return:
        """
        result = ProductCollection()
        self._get_products_with_dependencies(product_collection, result)
        #result.reverse()
        return result

    def _get_products_with_dependencies(self, products: ProductCollection, result: ProductCollection):
        """
        вспомогательная рекурсивная функция для поиска зависимостей
        :param products:
        :param result:
        :return:
        """
        if not products:
            logging.debug("products is None")
            return

        for p in products:
            if not result.product_in_coll(p):
                result.add_product(p)
                logging.debug("Added '{0}'".format(p.get_product_with_version()))

                dependencies = self.get_dependencies_for_product(p)
                if dependencies and len(dependencies) > 0:
                    # recursion !
                    for dep in dependencies:
                        logging.debug("\tdependant from: '{0}'".format(dep.get_product_with_version()))
                    self._get_products_with_dependencies(dependencies, result)

    def get_dependencies_for_product(self, product: BaseProduct):
        """
        для онкретного продукта получить его зависимости, без рекурсии
        :param product:
        :return:
        """
        if not product:
            return None

        # logging.debug("Get dependency for '{0}'".format(product))
        dependencies_names = product.get_dependencies()

        dependencies = ProductCollection()

        if not dependencies_names:
            # logging.debug("There are no dependencies for '{0}'".format(product))
            pass
        else:
            for name in dependencies_names:
                if isinstance(name, list):
                    name = self.get_first_or_installed(name)
                    logging.debug("choice dependence '{0}'".format(name))
                dependent_product = self.core.feed.get_product_or_exception(name)
                dependencies.add_product(dependent_product)

        return dependencies

    def get_engine(self, products: ProductCollection):
        """
        найти енжайн в этой колеекции
        :param products:
        :return:
        """
        for product in products:
            if isinstance(product, Engine):
                return product
        return None

    @staticmethod
    def remove_installed(products: ProductCollection, strict_version=True):
        """
        удалить из списка продуктов, те что уже установлены
        используется для фильтра перед install
        :param products:
        :param strict_version:
        :return:
        """
        logging.debug('input product list: {0}'.format(products))
        result = ProductCollection()
        for p in products:
            if strict_version:
                if not p.is_installed():
                    result.append(p)
            else:
                if not p.is_installed_any_version():
                    result.append(p)

        logging.debug('result product list: {0}'.format(result))
        return result

    def remove_not_installed(self, products: ProductCollection):
        """
        удалить из списка продуктов, те что еще не установлены
        используется для фильтра перед uninstall
        :param products:
        :return:
        """
        logging.debug(products)
        result = ProductCollection()
        for p in products:
            if self.core.current_storage.is_product_installed(p.get_product_with_version()):
                result.append(p)

        logging.debug(result)
        return result




    def get_first_or_installed(self, product_alternatives):
        """
        в списке продуктов найти первый который установлен
        или просто первый в списке

        использовался в первой версии поиска нужного энжайна
        теоеретически должен работать в консольной версии,
        там где нет возможности явно задать выбор
        :param product_alternatives:
        :return: :raise Exception:
        """
        if not product_alternatives:
            raise Exception("Empty product_alternatives")

        for product_name in product_alternatives:
            if self.core.current_storage.is_product_installed(product_name):
                return product_name

        return product_alternatives[0]

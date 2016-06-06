# -*- coding: utf-8 -*-

import logging
import os.path

from core.core import Core
from core.helpers.urls import combine_virtual_path
from core.models.application import Application
from core.models.product import Product
from core.models.engine import Engine
from core.parameters_manager import ParametersManager, KnownParameters
from core.product_collection import ProductCollection


class InstallManagerError(Exception):
    pass


class InstallManager(object):
    """
    вспомогательный класс, подготавливает окружение для выполнения команд
    -install
    -uninstall
    -upgrade

    """
    def __init__(self, products: ProductCollection, parameters_manager: ParametersManager=None):
        self.core = Core.get_instance()
        self.products = products
        self.pm = parameters_manager

    def __repr__(self):
        return 'InstallManager(product_list={0})'.format(self.products)


    def process_webserver_parameters(self, parameters):
        """
        для Application
        расчитать спецефические переемнные SITE_NAME, SITE_BINDING, CREATE_APP, PHYSICAL_PATH
        :param parameters:
        :raise Exception:
        """

        if parameters.get(KnownParameters.CREATE_SITE.value, False):
            if not all([
                (KnownParameters.SITE_NAME.value in parameters),
                # (KnownParameters.SITE_PATH.value in parameters),
                (KnownParameters.SITE_BINDING.value in parameters)
            ]):
                raise Exception("Please specify all parameters for create-site")

            self.core.api.os.web_server.site_create_from_dict(parameters)

        # pool
        if parameters.get(KnownParameters.CREATE_POOL.value, False):
            self.core.api.os.web_server.pool_create_from_dict(parameters)

        # application
        if parameters.get(KnownParameters.CREATE_APP.value, False):
            if not all([
                (KnownParameters.SITE_NAME.value in parameters),
                (KnownParameters.APP_NAME.value in parameters),
            ]):
                raise Exception("Please specify all parameters for create-app")

            self.core.api.os.web_server.application_create_from_dict(parameters)

        if KnownParameters.SITE_NAME.value in parameters:
            # set / if doesn't exist
            parameters[KnownParameters.APP_NAME.value] = parameters.get(KnownParameters.APP_NAME.value, "/")

            virtual_path = combine_virtual_path(
                parameters[KnownParameters.SITE_NAME.value],
                parameters.get(KnownParameters.APP_NAME.value))

            physical_path = self.core.api.os.web_server.map_webserver_path(virtual_path)

            if physical_path is None:
                raise Exception("Can't get physical_path for '{0}'".format(virtual_path))

            parameters[KnownParameters.PHYSICAL_PATH.value] = physical_path

    @staticmethod
    def check_database_parameters(parameters):
        """
        Проверить переданы ли все параметры для базы данных
        :param parameters:
        :raise Exception:
        """
        if not all([
            (KnownParameters.DB_HOST.value in parameters),
            (KnownParameters.DB_PORT.value in parameters),
            (KnownParameters.DB_NAME.value in parameters),
            (KnownParameters.DB_PASSWORD.value in parameters),
            (KnownParameters.DB_PASSWORD.value in parameters)
        ]):
            raise Exception("Please specify all parameters for database")

    def get_selected_engine_from_parameters(self, parameters) -> Engine:
        """
        найти выбраный энжайн в параметрах
        :param parameters:
        :return:
        """
        if KnownParameters.SELECTED_ENGINE.value in parameters:
            engine_name = parameters[KnownParameters.SELECTED_ENGINE.value]
            if engine_name:
                return self.core.engine_storage.get_product(engine_name)
        return None

    def set_install_dir(self, product: Product, parameters: dict):
        """
        выставить параметр INSTALL_DIR, если не указан явно - расчитать относительно zoo_home
        :param product:
        :param parameters:
        :return:
        """
        zoo_home = self.core.settings.zoo_home
        if zoo_home:
            install_dir = os.path.join(zoo_home, product.name)
            parameters[KnownParameters.INSTALL_DIR.value] = install_dir
            return
        if not KnownParameters.INSTALL_DIR.value in parameters:
            parameters[KnownParameters.INSTALL_DIR.value] = None

    def install(self):
        """
        установить все продукты в self.products
        в products теперь только один продукт
        передать продукту все параметры
        если это Application
        добавить доп параметры, и создать zoo конфиг в конце

        :return: :raise Exception:
        """
        # particulary do nothing
        self.core.update_environment_vars()
        logging.debug('products to install: {0}'.format(self.products.to_dict()))
        if not self.products:
            logging.warning('nothing to install')
            return
# product contain only one element in future we will avoid of it
        for product in self.products:

            parameters = None
            parameters = self.pm.get_for_product_flat(product)
            # process install-dir
            if isinstance(product, (Product, Engine)):
                self.set_install_dir(product, parameters)

            # process web server & db parameters
            if isinstance(product, Application):
                self.process_webserver_parameters(parameters)
                if product.database_type:
                    self.check_database_parameters(parameters)

                engine = self.get_selected_engine_from_parameters(parameters)
                if engine:
                    product.set_select_engine(engine)



            if product.install(parameters):
                    self.core.set_product_installed(product, parameters)
        return parameters


    def upgrade(self):
        """


        :return:
        """
        self.core.update_environment_vars()
        if not self.products:
            logging.warning('nothing to upgrade')
            return

        logging.debug('products to upgrade: {0}'.format(self.products.to_dict()))

        for product in self.products:
            parameters = self.pm.get_for_product_flat(product)

            # process install-dir
            if isinstance(product, Product):
                self.set_install_dir(product, parameters)

            # process web server & db parameters
            if isinstance(product, Application):
                self.process_webserver_parameters(parameters)
                if product.database_type:
                    self.check_database_parameters(parameters)

            if product.is_installed_any_version():
                if product.upgrade(parameters):
                    self.core.set_product_installed(product, parameters)
            else:
                if product.install(parameters):
                    self.core.set_product_installed(product, parameters)

        logging.debug('upgrade completed')

    def uninstall(self):
        """
        удалить все продукты в self.products

        :return:
        """
        if not self.products:
            logging.warning('nothing to uninstall')
            return

        logging.debug('products to uninstall: {0}'.format(self.products.pformat()))
        for product in self.products:
            if product.uninstall():
                self.core.set_product_uninstalled(product)

        logging.debug('uninstallation completed')


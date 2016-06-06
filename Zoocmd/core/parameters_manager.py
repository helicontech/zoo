# -*- coding: utf-8 -*-

import logging
from collections import OrderedDict
from enum import Enum

from core.models.product_parameter import ProductParameter


class ParametersManagerError(Exception):
    pass


class KnownParameters(Enum):
    """
    известные зу параметры для приложений
    их необязательно задавать явно в приложении, они все-равно будут расчитаны и переданы в него, если нужно
    """
    
    # web site
    CREATE_SITE = 'create-site'          # нужно ли создавать сайт, если не нужно, то указать существующий
    SITE_NAME = 'site-name'              # имя сайта
    #SITE_PATH = 'site-path'
    SITE_BINDING = 'site-binding'        # строка для указания биндингов, нужно только если сайт нужно создавать

    # web app
    CREATE_APP = 'create-app'            # нужно ли создавать приложение в иисе? если не нужно, то указать существующее
    APP_NAME = 'app-name'                # имя приложения
    SELECTED_ENGINE = 'selected-engine'  # какой использовать энжайн для приложения

    # web app pool
    CREATE_POOL = 'create-app-pool'     # нужно ли создавать пул в иисе? или взять существующий
    POOL_NAME = 'app-pool-name'         # имя пула
    POOL_DOT_NET = 'app-pool-dot-net'   # если пул содается. нужно указать версию дотнета, 2.0 или 4.5

    # paths
    PHYSICAL_PATH = 'physical-path'     # физический путь к диретории куда будет установлено приложение
    INSTALL_DIR = 'install_dir'         # физический путь к диретории куда будет установлен продукт
    
    # database connection
    DB_ENGINE = 'db-engine'             # наверное это тип базы данных, mysql, sqllite нигде пока не используется
    DB_HOST = 'db-host'                 # хост если есть
    DB_PORT = 'db-port'                 # порт если есть
    DB_USERNAME = 'db-username'         # имя пользователя
    DB_PASSWORD = 'db-password'         # пароль
    DB_NAME = 'db-name'                 # имя базы данных


class ParametersManager(object):
    """
    менеджер параметров,
    умеет жонглировать параметрами
    ему передаются все параметры как есть, а он добывает для конкретного приложения
    расчитывает значения KnownParameters
    """
    def __init__(self, core_instance, products, input_parameters=None):
        self.core = core_instance
        self.products = products
        if input_parameters is None:
            self.input_parameters = OrderedDict()
        else:
            self.input_parameters = input_parameters
        self.parameters = self.compute_all_parameters()
        self.failed_parameters = []
        logging.debug(self)

    def __repr__(self):
        return 'ParameterManager(input_parameters={0})'.format(self.input_parameters)

    def get_input_value(self, product_name, parameter_name):
        """
        получить введенное пользователем значение для указанного параметра, для указанного продукта

        input_parameters:
            wordpress:
                site-name: test wordpress 6301
                app-virtual-path: /blog 1
            php:
                path: 111
        """
        input_value = None
        if product_name in self.input_parameters:
            parameters_for_product = self.input_parameters[product_name]
            input_value = parameters_for_product.get(parameter_name, None)

        # it's looks like a VERY STRANGE HACK !!!
        if input_value is None:
            if None in self.input_parameters:
                parameters_for_all_products = self.input_parameters[None]
                input_value = parameters_for_all_products.get(parameter_name, None)

        return input_value



    def compute_all_parameters(self):
        """
        расчитать все параметры для всех продуктов

        :return:
        """
        products_parameters_dict = OrderedDict()

        for product in self.products:
            product_name = product.name.lower()
            products_parameters_dict[product_name] = self.get_product_parameters_list(product)

        return products_parameters_dict

    def get_product_parameters_list(self, product):
        """
        вернуть все параметры для указанного продукта в виде списка значений ProductParameter()

        :param product:
        :return:
        """
        product_parameters_list = []
        product_name = product.name.lower()

        auto_default_params = OrderedDict()
        # using iisexpress with application
        if self.core.platform.web_server == "iisexpress" and "application" == product.get_typename():
            auto_default_params = self.core.api.os.web_server.get_default_site_params(product_name)

        if "application" == product.get_typename():
            auto_default_params[KnownParameters.SELECTED_ENGINE.value] = product.engines[0]['engine']

        # known parameters
        for known_param_name in KnownParameters:
            # get user input
            value = self.get_input_value(product_name, known_param_name.value)
            if value:
                product_parameter = ProductParameter(product_name, known_param_name.value, None)
                product_parameter.set(value)
                product_parameters_list.append(product_parameter)
            else:
                # ok use our auto default values if exists
                if auto_default_params is not None and known_param_name.value in auto_default_params:
                    product_parameter = ProductParameter(product_name, known_param_name.value, None)
                    product_parameter.set(auto_default_params[known_param_name.value])
                    product_parameters_list.append(product_parameter)

        # product input params
        product_input_parameters = None
        if product_name in self.input_parameters:
            product_input_parameters = self.input_parameters[product_name]

        # application parameters
        # also notice we override auto default params and calculated params
        if product.parameters:
            for param_name in product.parameters:
                default_value = product.parameters[param_name]
                # try to find param value in input params if its existed
                if product_input_parameters:
                    if param_name in product_input_parameters:
                        default_value = product_input_parameters[param_name]
                product_parameter = ProductParameter(product_name, param_name, default_value)
                # get user input
                value = self.get_input_value(product_name, param_name)
                if value:
                    product_parameter.set(value)
                else:
                    product_parameter.set(default_value)

                product_parameters_list.append(product_parameter)

        return product_parameters_list

    def get_for_product(self, product):
        """
        Returns list of ProductParameter objects

        :rtype : list
        """
        product_name = product.name.lower()

        if not product_name in self.parameters:
            raise ValueError('No parameters for {0}'.format(product_name))

        result = []

        # get product-specified parameters
        result.extend(self.parameters[product_name])

        logging.debug('{0} parameters:{1}'.format(product_name, result))
        return result

    def get_for_product_flat(self, product):
        """
        вернуть параметры для продуктов в виде словаря

        :param product:
        :return:
        """
        result = OrderedDict()
        product_parameters = self.get_for_product(product)
        for product_parameter in product_parameters:
            result[product_parameter.name] = product_parameter.value
        return result




    def are_all_parameters_filled(self):
        """
        проверить заполнены ли все параметры для всех продуктов
        если нет, то ошибка, если  спросить нельзя

        :return:
        """
        self.failed_parameters = []
        for product in self.products:
            product_parameters = self.get_for_product(product)
            if product_parameters:
                for product_parameter in product_parameters:
                    if product_parameter.error:
                        self.failed_parameters.append(product_parameter)

        return len(self.failed_parameters) == 0

    def ask_unfilled_parameters(self):
        """
        спросить у пользователя недостающие параметры

        :return:
        """
        if not self.failed_parameters:
            return
        logging.info('Please specify following parameters to proceed with installation')
        for product_parameter in self.failed_parameters:
            product_parameter.query()

    def raise_parameters_error(self):
        """
        хелпер. Выбросить исключение для незаполненных параметров

        :raise ValueError:
        """
        if self.failed_parameters:
            raise ValueError('Following parameters must be filled: {0}'.format(self.failed_parameters))

    def get_error(self, product):
        """
        Получить строку для ошибки. показать какие параметры незаполнены

        :param product:
        :return:
        """
        product_parameters = self.get_for_product(product)
        failed_parameters = []
        if product_parameters:
            for product_parameter in product_parameters:
                if product_parameter.error:
                    failed_parameters.append(product_parameter.name)

        if failed_parameters:
            return 'Please check {0} parameter{1}'.format(
                ', '.join(failed_parameters),
                's' if len(failed_parameters) else ''
            )

        return None

    def get_state(self):
        """
        example of returned state:
        wordpress:
          virtual_path: path1
          user_name: user1
        mysql:
          install_path: path2
        """
        output_parameters = OrderedDict()

        for product_name, product_parameters_list in self.parameters.items():
            parameters_dict = OrderedDict()
            for product_parameter in product_parameters_list:
                parameters_dict[product_parameter.name] = product_parameter.value
            output_parameters[product_name] = parameters_dict

        return output_parameters


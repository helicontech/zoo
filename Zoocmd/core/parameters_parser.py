# -*- coding: utf-8 -*-

from collections import OrderedDict
import logging
import re
from core.helpers.yaml_helper import YamlHelper
from core.helpers.common import  json_decode_file

class ParametersParserBase(object):
    """
    Разбор параметров.
    на выходе должен быть словарь параметров, готовый к использованию в Core
    """
    def __init__(self):
        self.parameters = OrderedDict()

    def get(self):
        return self.parameters


class EmptyParameters(object):
    """
    Генерим пустые параметры для списка параметров
    полезно
    """
    def __init__(self):
        self.parameters = OrderedDict()

    def get(self, product_list):
        for i in product_list:
            if isinstance(i, dict):
                self.parameters[i["name"]] = OrderedDict()
            elif isinstance(i, str):
                self.parameters[i] = OrderedDict()
            else:
                raise RuntimeError("Invalid arguments of product list")

        return self.parameters


class ParametersParserJsonFile(ParametersParserBase):
    """
    Разбор параметров из Json. Используется в UI
    """

    def __init__(self,   filename):
        super().__init__()
        self.filename = filename
        self.parameters = self.parse_jsonfile()

    def parse_jsonfile(self):
        decoded = json_decode_file(self.filename)
        result = OrderedDict()
        for item in decoded:
            if 'product' in item and 'parameters' in item and item['parameters']:
                product_name = item['product']
                if product_name:
                    product_name = product_name.lower()
                if not product_name in result:
                    result[product_name] = OrderedDict()
                for param_name, param_value in item['parameters'].items():
                    result[product_name][param_name] = param_value
        return result



class ParametersParserYmlFile(ParametersParserBase):
    """
    Разбор параметров из Json. Используется в UI
    """

    def __init__(self,  filename):
        super().__init__()
        self.filename = filename
        self.parameters = self.parse_ymlfile()

    def parse_install_request(self):
        decoded = YamlHelper.load_from_file(self.filename)
        result = OrderedDict()
        for item in decoded:
            if 'product' in item and 'parameters' in item and item['parameters']:
                product_name = item['product']
                if product_name:
                    product_name = product_name.lower()
                if not product_name in result:
                    result[product_name] = OrderedDict()
                for param_name, param_value in item['parameters'].items():
                    result[product_name][param_name] = param_value
        return result


class ParametersParserJson(ParametersParserBase):
    """
    Разбор параметров из Json. Используется в UI
    """

    def __init__(self, install_request):
        super().__init__()
        self.install_request = install_request
        self.parameters = self.parse_install_request()

    def parse_install_request(self):
        result = OrderedDict()
        for item in self.install_request:
            if 'product' in item and 'parameters' in item and item['parameters']:
                product_name = item['product']
                if product_name:
                    product_name = product_name.lower()
                if not product_name in result:
                    result[product_name] = OrderedDict()
                for param_name, param_value in item['parameters'].items():
                    result[product_name][param_name] = param_value
        return result


class ParametersParserStr(ParametersParserBase):
    """Parse install parameters from command line.
    Format:
    --parameters param1=val1 product2@param2=val2 ...
    """
    PARAMETER_RE = re.compile(r'(?:([\w\._-]+)@)?([\w\._-]+)=(.*)')

    def __init__(self, raw_str):
        super().__init__()
        self.raw_str = raw_str
        self.parameters = self.parse_raw_string()

    def parse_raw_string(self):
        result = OrderedDict()
        if self.raw_str:
            for raw_parameter_str in self.raw_str:
                m = self.PARAMETER_RE.match(raw_parameter_str)
                if m:
                    product = m.group(1)
                    if product:
                        product = product.lower()
                    name = m.group(2)
                    value = m.group(3)
                    if not product in result:
                        result[product] = OrderedDict()
                    result[product][name] = value

        logging.debug("'{0}' -> {1}".format(self.raw_str or '', result))
        return result

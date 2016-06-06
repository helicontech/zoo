# -*- coding: utf-8 -*-

from .installer_apis.windows import WindowsApi
from .installer_apis.python import PythonApi
from .installer_apis.os import OsApi
from .installer_apis.iis import IISApi


class InstallerApi(object):
    """
    апи доступные для 'install_command'
    """

    def __init__(self, core, product):
        self.core = core
        self.product = product
        self.windows = WindowsApi(self.core, self.product)
        self.python = PythonApi(self.core, self.product)
        self.os = OsApi(self.core, self.product)
        self.iis = IISApi(self.core, self.product)

    def get_api(self):
        apis = {
            'windows': self.windows,
            'python': self.python,
            'os': self.os,
            'iis': self.iis
        }

        return apis

# -*- coding: utf-8 -*-

import os
import os.path
import logging


class PythonApi(object):
    """
    Helper class for installing python apps.
    Instance with name 'python' is available in install_commands.
    Example:
    python.create_virtual_env()
    """

    python_install_path = None

    def __init__(self, core, product):
        """
        Saves products and search python install dir.
        """
        self.core = core
        self.product = product

        if PythonApi.python_install_path is None:
            PythonApi.python_install_path = \
                self.core.api.os.registry.read(r'HKLM\SOFTWARE\Python\PythonCore\2.7\InstallPath', '') or \
                self.core.api.os.registry.read(r'HKLM\SOFTWARE\Python\PythonCore\2.7\InstallPath', '', 32) or ''

    def _check_python_install_path(self):
        if not self.python_install_path:
            raise RuntimeError('python install path not found')

    #
    def create_virtual_env(self, path, name='venv'):
        """
        Creates virtual env for installing zoo app if not exist.
        Example:
        :param path: zoo app path
        :param name: virtual env name
        """
        self._check_python_install_path()
        path = self.core.expandvars(path, self.product)
        venv_path = os.path.join(path, name)
        if not os.path.exists(venv_path):
            virtualenv_exe = os.path.join(self.python_install_path, 'scripts', 'virtualenv.exe')
            command = '{0} "{1}"'.format(virtualenv_exe, venv_path)
            self.core.api.os.shell.cmd(command)
        else:
            logging.debug('virtualenv {0} already exists'.format(venv_path))

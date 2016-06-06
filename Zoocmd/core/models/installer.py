# -*- coding: utf-8 -*-

import logging
import re
import os.path
import sys
from core.models.installed_product import InstalledProductInfo
from ..installer_api import InstallerApi
import traceback
from core.exception import TaskException

class Installer(object):
    """
    Helper class that allows to call install_command, upgrade_command,
    uninstall_command and find_installed_command for product.
    Every product has instance of this class named 'installer'.
    """

    def __init__(self, product, install_command, upgrade_command, uninstall_command, find_installed_command):
        # set product and core
        self.product = product
        self.core = product.core

        # set commands
        self.install_command = install_command
        self.upgrade_command = upgrade_command
        self.uninstall_command = uninstall_command
        self.find_installed_command = find_installed_command

        # create installer api,
        # attributes from this object will be available in commands runtime: os, iis, windows, python.
        self.installer_api = InstallerApi(self.core, self.product)

        # local variables for command sruntime
        self.local = {
            'core': self.core,
            self.product.get_typename(): self.product,
            're': re,
            'InstalledProductInfo': InstalledProductInfo,
            'self': product
        }

        # update local variables with installer api objects (os, iis, windows, python)
        self.local.update(self.installer_api.get_api())

    def install(self, parameters: dict)-> bool:
        """
        Calls install_command for product.
        :param parameters: install parameters for product
        """
        if self.install_command is None:
            logging.info('no install_command for {0}'.format(self.product))
            return True

        logging.info('Installing {0}'.format(self.product))
        logging.debug('command: {0}'.format(self.install_command))

        # create copy of local variables for command runtime
        local = self.local.copy()
        # update local variable with files list
        local['files'] = self.product.files
        # update local variable with parameters
        local['parameters'] = parameters

        # fill default log dir
        local["os"].setup_log_dir()
        try:
            # execute install_command with local variables placed in 'local'
            exec(self.install_command, None, local)
        except:
            message = "Can't execute install command  {0}".format(self.product)
            raise TaskException(message, self.product, traceback.format_exc())

        return True

    def upgrade(self, parameters)-> bool:
        """
        Calls upgrade_command for product.
        :param parameters: install parameters for product
        """
        if self.upgrade_command is None:
            logging.info('no upgrade_command for {0}'.format(self.product))
            return True

        logging.info('Upgrading {0}'.format(self.product))
        logging.debug('command: {0}'.format(self.upgrade_command))

        # create copy of local variables for command runtime
        local = self.local.copy()
        # update local variable with files list
        local['files'] = self.product.files
        # update local variable with parameters
        local['parameters'] = parameters

        # fill default log dir
        local["os"].setup_log_dir()

        # execute upgrade_command with local variables placed in 'local'

        try:
            # execute install_command with local variables placed in 'local'
            exec(self.upgrade_command, None, local)
        except:
            message = "Can't  execute upgrade command  {0}".format(self.product)
            raise TaskException(message, self.product, traceback.format_exc())

        return True

    def uninstall(self):
        """
        Calls uninstall_command for product.
        """
        if self.uninstall_command is None:
            logging.info('There is no uninstall_command for {0}'.format(self.product))
            return True

        logging.info('Uninstalling {0}'.format(self.product))
        logging.debug('command: {0}'.format(self.uninstall_command))

        # create copy of local variables for command runtime
        local = self.local.copy()
        # update local variable with files list
        local['files'] = self.product.files
        # update local variable with parameters
        local['parameters'] = self.product.parameters

        # fill default log dir
        local["os"].setup_log_dir()

        try :
            # execute uninstall_command with local variables placed in 'local'
            exec(self.uninstall_command, None, local)
        except:
            message = "Can't  execute uninstall command   {0}".format(self.product)
            raise TaskException(message, self.product, traceback.format_exc())

        return True

    def find_installed(self):
        """
        Calls find_installed_command for product.
        Assumes that find_installed_command alway
s exists.
        """
        # create copy of local variables for command runtime
        local = self.local.copy()
        # update local variable with files list
        local['files'] = self.product.files
        # update local variable with parameters
        local['parameters'] = self.product.parameters
        # local['ZOO_HOME'] = self.core.settings.zoo_home

        # execute result with local variables placed in 'local'
        exec(self.find_installed_command, None, local)
        # return result of execution in 'result' command local variables
        return local.get('result')

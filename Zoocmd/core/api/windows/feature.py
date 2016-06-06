# -*- coding: utf-8 -*-

import logging
import os


class WindowsFeature():
    """
    Api to install or uninstall windows features (IIS, .Net, ...)
    """


    def __init__(self, core):
        self.core = core
        """
        Not needed anymore as we start 64-bit version of cmd.exe anyway

        _dism_exe = self.core.expandvars(r'%SystemRoot%\Sysnative\dism.exe')
        if os.path.isfile(_dism_exe):
            self.dism_exe = _dism_exe
        else:
            _dism_exe = self.core.expandvars(r'%SystemRoot%\System32\dism.exe')
            if os.path.isfile(_dism_exe):
                self.dism_exe = _dism_exe
        """


    def install(self, name):
        """
        Install Windows feature
        :param name: feature name
        """
        logging.info("Install windows feature: '{0}'".format(name))
        return self.core.api.os.shell.cmd('dism.exe /Online /NoRestart /Enable-Feature /FeatureName:{0}'.format(name))

    def uninstall(self, name):
        """
        Uninstall Windows feature
        :param name: feature name
        """
        logging.info("Uninstall windows feature: '{0}'".format(name))
        return self.core.api.os.shell.cmd("dism.exe /Online /NoRestart /Disable-Feature /FeatureName:{0}".format(name), ignore_exit_code=True)



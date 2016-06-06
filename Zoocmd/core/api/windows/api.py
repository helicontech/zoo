# -*- coding: utf-8 -*-

from core.api.windows.registry import Registry
from core.api.windows.msi_manager import MsiManager
from core.api.windows.shell import WindowsShell
from core.api.windows.feature import WindowsFeature
from core.api.windows.security import SecurityApi
from ..webservers.manager import WebServerManager


class WindowsApi():
    """
    Container of all api objects.
    """

    def __init__(self, core):
        self.msi = MsiManager()
        self.registry = Registry()
        self.shell = WindowsShell(core.settings.root)
        self.feature = WindowsFeature(core)
        webserver_manager = WebServerManager(core)
        self.web_server = webserver_manager.get_webserver_api()
        self.security = SecurityApi(core)


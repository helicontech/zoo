# -*- coding: utf-8 -*-

from core.api.windows.api import WindowsApi


class ApiManager:
    """
    Represents API collection inside Core.
    The collection has one api object 'os' now.
    Collection may be extended in future.
    """
    def __init__(self, core):
        self.core = core
        self.os = WindowsApi(self.core)



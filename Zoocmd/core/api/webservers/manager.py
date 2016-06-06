# -*- coding: utf-8 -*-

import logging

from .base import BaseWebServer
from .noserver import NoWebServer
from .iis import IIS


class WebServerManager(object):
    """
    Creates web server api by specified webserver in platform
    """

    def __init__(self, core):
        self.core = core
        self.platform_webserver = self.core.platform.web_server

    def get_webserver_api(self) -> BaseWebServer:
        webserver_api = None

        if self.platform_webserver == 'iis':
            if IIS.is_installed():
                # iis
                webserver_api = IIS(self.core, False)
        elif self.platform_webserver == 'iisexpress':
            # iis express
            webserver_api = IIS(self.core, True)
        else:
            # no webserver specified in platform
            # search it!
            if IIS.is_installed():
                webserver_api = IIS(self.core, False)

        if not webserver_api:
            webserver_api = NoWebServer()

        logging.debug('web server api created: {0}'.format(webserver_api.__class__.__name__))
        return webserver_api
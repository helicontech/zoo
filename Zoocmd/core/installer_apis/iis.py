# -*- coding: utf-8 -*-


class IISApi(object):
    """
    Web server api helper.
    Instance with name 'iis' is available in install_commands.
    Example:
    iis.map_webserver_path(...)
    """

    def __init__(self, core, product):
        self.core = core
        self.product = product

    def map_webserver_path(self, virtual_path):
        """
        Returns physical path for virtual path.
        """
        path = self.core.api.os.web_server.map_webserver_path(virtual_path)
        if not path:
            raise FileNotFoundError(virtual_path)
        return path

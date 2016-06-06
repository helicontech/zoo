# -*- coding: utf-8 -*-

from .base import BaseWebServer


class NoWebServer(BaseWebServer):
    """
    Implementation of BaseWebServer interface when any web server not found
    """

    def get_app_pool_list(self) -> list:
        return []

    def get_list_of_sites(self) -> list:
        return []

    @staticmethod
    def get_zoo_config(physical_path):
        return {}

    def get_server_node(self):
        return {
            'name': '',
            'path': '',
            'type': 'server'
        }

    def get_directories(self, site_name, virt_path):
        return []


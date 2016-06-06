# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class BaseWebServer(object):
    """
    Abstract base class for web server api
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_directories(self, site_name, virt_path):
        pass

    @abstractmethod
    def get_server_node(self):
        """
        returns dict for server tree (for ui)
        """
        pass

    @staticmethod
    @abstractmethod
    def get_zoo_config(physical_path):
        raise NotImplemented

    @abstractmethod
    def get_list_of_sites(self) -> list:
        pass

    @abstractmethod
    def get_app_pool_list(self) -> list:
        pass
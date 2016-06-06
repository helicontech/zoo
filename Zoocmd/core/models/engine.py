# -*- coding: utf-8 -*-

from core.models.base_product import BaseProduct
from collections import OrderedDict

class Engine(BaseProduct):
    """
    Represents Engine product type.
    Differences from BaseProduct:
    - addition attribute 'config'
    - search installed version in engine storage, not current storage
    """
    def __init__(self, core, attrs = None):
        super().__init__(core, attrs)
        # new attribute
        self.config = OrderedDict()

    def get_typename(self):
        return "engine"

    def merge(self, **kwargs):
        super().merge(**kwargs)
        # merge new attribute
        self.config = kwargs.get('config') or self.config


    def __getstate__(self):
        result = super().__getstate__()
        result['config'] = self.config
        return result

    def get_installed_version(self):
        """
        Returns installed version from engine storage (not current storage!)
        """
        if not self.installed_version:
            if self.core.engine_storage:
                synced_product = self.core.engine_storage.feed.get_product(self.name)
                if synced_product:
                    self.installed_version = synced_product.installed_version
                    self.config = synced_product.config
        return self.installed_version

    def update_config(self):
        """
        Обновить свой конфиг из engines.yaml
        """
        if self.is_installed():
            synced_product = self.core.engine_storage.feed.get_product(self.name)
            if synced_product:
                self.config = synced_product.config

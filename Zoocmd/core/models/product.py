# -*- coding: utf-8 -*-

from core.models.base_product import BaseProduct


class Product(BaseProduct):
    """
    Represents Product class.
    Repeats the base class behaviour.
    """
    def get_typename(self):
        return "product"

# -*- coding: utf-8 -*-

import unittest

from core.core import Core
from core.models.product import Product


class ProductMainAction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core.get_instance()

    def test_download(self):
        pass

    def test_install(self):
        pass

    def test_two_versions(self):
        pass
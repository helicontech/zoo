# -*- coding: utf-8 -*-
from core import start

import unittest

from core.core import Core

class FeedLoaderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core.get_instance()

    def runTest(self):
        self.test_loader()
        self.test_products()

    def test_loader(self):
        self.assertIsInstance(self.core.feed.raw_collection, list)
        self.assertGreater(len(self.core.feed.raw_collection), 0)

    def test_products(self):
        for product in self.core.feed.get_products():
            self.assertIsNotNone(product.name, msg=product)
            self.assertIsNotNone(product.title, msg=product)
            self.assertIsNotNone(product.description, msg=product)
            self.assertIsNotNone(product.link, msg=product)
            self.assertIsNotNone(product.author, msg=product)
            self.assertIsNotNone(product.platform, msg=product)
            self.assertTrue(product.platform.os.startswith('windows'), msg=product)
            self.assertTrue(product.os.startswith('windows'), msg=product)
            self.assertIsNotNone(product.version, msg=product)



# -*- coding: utf-8 -*-

import unittest

from core.core import Core


class BucketTests(unittest.TestCase):


    def runTest(self):
        self.test_get_products()
        self.test_get_product_success()
        self.test_get_product_fail()


    @classmethod
    def setUpClass(cls):

        cls.core = Core.get_instance()

        cls.core.feed.raw_collection.append(dict(product='x', os='windows', title='X'))
        cls.core.feed.raw_collection.append(dict(product='x', os='windows', bitness='64', version='1.3.5'))
        cls.core.feed.raw_collection.append(dict(product='x', os='windows', bitness='64', version='1.3.7'))
        cls.core.feed.raw_collection.append(dict(product='x', os='windows', bitness='64', version='1.3.9'))

        cls.core.feed.raw_collection.append(dict(product='y'))
        cls.core.feed.raw_collection.append(dict(product='y', os='windows', bitness='64', version='1.5.0'))
        cls.core.feed.raw_collection.append(dict(product='y', os='windows', bitness='64', version='1.5.2'))
        cls.core.feed.raw_collection.append(dict(product='y', os='windows', bitness='64', version='1.5.4'))

    def test_get_products(self):
        products = self.core.feed.get_products()
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].name, 'x')
        self.assertEqual(products[0].version, '1.3.9')
        self.assertEqual(products[1].name, 'y')
        self.assertEqual(products[1].version, '1.5.4')

    def test_get_product_success(self):
        p1 = self.core.feed.get_product('y')
        self.assertEqual(p1.name, 'y')
        self.assertEqual(p1.version, '1.5.4')

        p2 = self.core.feed.get_product('x==1.3.7')
        self.assertEqual(p2.name, 'x')
        self.assertEqual(p2.version, '1.3.7')

        p3 = self.core.feed.get_product('x>=1.3.5')
        self.assertEqual(p3.name, 'x')
        self.assertEqual(p3.title, 'X')
        self.assertEqual(p3.version, '1.3.9')

        p4 = self.core.feed.get_product('y<1.5.1')
        self.assertEqual(p4.name, 'y')
        self.assertEqual(p4.version, '1.5.0')

    def test_get_product_fail(self):
        self.assertIsNone(self.core.feed.get_product('z'))
        self.assertIsNone(self.core.feed.get_product('q==1.3.5.6'))

        self.assertIsNone(self.core.feed.get_product('x==1.3.4'))
        self.assertIsNotNone(self.core.feed.get_product('x==1.3.5'))
        self.assertIsNone(self.core.feed.get_product('x==1.3.6'))

        self.assertIsNone(self.core.feed.get_product('x<1.3.5'))
        self.assertIsNone(self.core.feed.get_product('x>1.3.9'))

    def test_remove_product(self):
        core = Core.create_instance(dict(os='windows', bitness='64'))

        core.feed.raw_collection.append(dict(product='x', os='windows'))
        core.feed.raw_collection.append(dict(product='x', os='windows', bitness='64', version='1.3.5'))
        core.feed.raw_collection.append(dict(product='x', os='windows', bitness='64', version='1.3.7'))

        core.feed.raw_collection.append(dict(product='y'))
        core.feed.raw_collection.append(dict(product='y', os='windows', bitness='64', version='1.5.0'))
        core.feed.raw_collection.append(dict(product='y', os='windows', bitness='64', version='1.5.2'))

        self.assertEqual(len(core.feed.raw_collection), 6)

        core.feed.remove_product('x')

        self.assertEqual(len(core.feed.raw_collection), 3)
        self.assertIsNone(core.feed.get_product('x'))
        self.assertIsNotNone(core.feed.get_product('y'))





# -*- coding: utf-8 -*-

import unittest

from core.core import Core
from core.dependency_manager import DependencyManager
from core.product_collection import ProductCollection

class DependenciesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core.get_instance()
        cls.core.feed.raw_collection.extend([
            {
                'product': 'P1',
                'version': '1.1'
            },
            {
                'product': 'P1',
                'version': '1.2',
            },
            {
                'application': 'A1',
                'dependencies': ['P1']
            },
            {
                'application': 'A2',
                'dependencies': ['P1==1.1']
            },
            {
                'product': 'P1',
                'version': '1.3',
            },
        ])

    def runTest(self):
        self.test_dependencies_versions1()
        self.test_dependencies_versions2()

    def test_dependencies_versions1(self):
        products = ProductCollection(['A1'])
        dm = DependencyManager()
        products = dm.get_products_with_dependencies(products)
        self.assertEqual(len(products), 2)
        p1 = products[0]
        self.assertEqual(p1.name, 'P1')
        self.assertEqual(p1.version, '1.3')
        a1 = products[1]
        self.assertEqual(a1.name, 'A1')

    def test_dependencies_versions2(self):
        products = ProductCollection(['A2'])
        dm = DependencyManager()
        products = dm.get_products_with_dependencies(products)
        self.assertEqual(len(products), 2)
        p1 = products[0]
        self.assertEqual(p1.name, 'P1')
        self.assertEqual(p1.version, '1.1')
        a1 = products[1]
        self.assertEqual(a1.name, 'A2')

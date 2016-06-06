import unittest

from core.core import Core
from core.models.product import Product
from core.version_comparer import VersionComparer, ProductComparer


class ProductCompareTests(unittest.TestCase):

    def runTest(self):
        self.test_match_product()
        self.test_match_version()
        self.test_two_versions()


    def test_match_version(self):
        self.assertTrue(VersionComparer('>', '1.0.0.0').match('2.0.0.0'))
        self.assertFalse(VersionComparer('>', '1.0.0.0').match('1.0.0.0'))
        self.assertTrue(VersionComparer('<', '1.0.0.0').match('0.0.0.0'))
        self.assertTrue(VersionComparer('<=', '1.0.0.0').match('1.0.0.0'))
        self.assertTrue(VersionComparer('>=', '1.0.0.0').match('1.0.0.0'))
        self.assertRaises(ValueError, VersionComparer, '?', '1.0.0.0')

    def test_match_product(self):
        p = Product(core=Core.get_instance())
        p.merge(product="Zoo", version="4.0")

        self.assertTrue(ProductComparer("zoo>3.0.0.1").match('zoo', '4.0'))
        self.assertFalse(ProductComparer("zoo>4.0").match('zoo', '4.0'))
        self.assertFalse(ProductComparer("foo>3.0").match('zoo', '4.0'))

    def test_two_versions(self):
        pc = ProductComparer('p>1.0,=<3.0')
        self.assertIsNotNone(pc.vc1)
        self.assertIsNotNone(pc.vc2)
        self.assertTrue(pc.match('p', '1.0.0.1'))
        self.assertTrue(pc.match('p', '2'))
        self.assertTrue(pc.match('p', '3.0'))
        self.assertFalse(pc.match('p', '1.0'))
        self.assertFalse(pc.match('p', '3.0.1'))
        self.assertFalse(pc.match('x', '2.0'))


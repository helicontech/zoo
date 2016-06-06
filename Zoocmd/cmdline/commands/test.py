from tests.test_product_compare import ProductCompareTests
from tests.test_api_windows import WindowsApiTests
from tests.test_apps import ApplicationLoaderTests
from tests.test_bucket import BucketTests
from tests.test_dependencies import DependenciesTests
from tests.test_parameters import ParametersTests
from tests.test_platform import PlatformTests
from tests.test_loader import FeedLoaderTests
import unittest


class RunTestCommand(object):

    def __init__(self, core):
        self.core = core

    def run(self):
        suite = unittest.TestSuite()
        suite.addTest(ProductCompareTests('test_match_version'))
        suite.addTest(ProductCompareTests('test_match_product'))
        suite.addTest(ProductCompareTests('test_two_versions'))

        suite.addTest(WindowsApiTests('test_registry_read'))
        suite.addTest(WindowsApiTests('test_set_system_env'))
        suite.addTest(WindowsApiTests('test_iis_api'))
        suite.addTest(WindowsApiTests('test_windows_installation_type'))

        suite.addTest(ApplicationLoaderTests('test_get_state'))


        suite.addTest(BucketTests('test_get_products'))
        suite.addTest(BucketTests('test_get_product_success'))
        suite.addTest(BucketTests('test_get_product_fail'))



        suite.addTest(DependenciesTests('test_dependencies_versions1'))
        suite.addTest(DependenciesTests('test_dependencies_versions2'))

        suite.addTest(FeedLoaderTests('test_loader'))
        suite.addTest(FeedLoaderTests('test_products'))

        suite.addTest(ParametersTests('test_parameters'))


        suite.addTest(PlatformTests('test_match'))
        suite.addTest(PlatformTests('test_os_version_match'))
        suite.addTest(PlatformTests('test_parse'))


        unittest.TextTestRunner().run(suite)



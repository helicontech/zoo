# -*- coding: utf-8 -*-

import unittest

from core.core import Core
from core.models.product import Product
from core.install_manager import InstallManager
from core.parameters_manager import ParametersManager
from core.parameters_parser import ParametersParserStr


class ParametersTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.core = Core.get_instance()

    def runTest(self):
        self.test_parameters()


    def test_parameters(self):
        pps = ParametersParserStr((
                'prod1@par3=r444',
                'par1=q111',
                'par2=w222',
                'prod1@par2=e333',
                'par3=t555'
            ))

        # params = pred_params.get_for_product('prod1')
        params = pps.parameters['prod1']

        self.assertEqual(len(params), 2)
        # self.assertIn('par1', params)
        # self.assertEqual(params['par1'], 'q111')
        self.assertIn('par2', params)
        self.assertEqual(params['par2'], 'e333')
        self.assertIn('par3', params)
        self.assertEqual(params['par3'], 'r444')

    # def test_product_parameters(self):
    #     product1 = Product(self.core)
    #     product1.merge(**{
    #         'product': 'prod1',
    #         'parameters': {
    #             'host': 'localhost',
    #             'port': '3306',
    #             'username': None,
    #             'password': None
    #         }
    #     })
    #
    #     product2 = Product(self.core)
    #     product2.merge(**{
    #         'product': 'prod2',
    #         'parameters': {
    #             'host': 'localhost',
    #             'port': '3306',
    #             'username': None,
    #             'password': None
    #         }
    #     })
    #
    #
    #     parameters_args = (
    #         (
    #             'prod1@host=host1',
    #             'prod2@host=host2',
    #             'foo=bar',
    #             'prod2@foo=bar2',
    #             'username=root'
    #         )
    #     )
    #
    #
    #     parameters = ParametersManager(raw_str=parameters_args)
    #     install_manager = InstallManager(self.core)
    #
    #     # product 1
    #     install_manager.fill_parameters(product1)
    #     product_parameters1 = product1.get_parameters()
    #
    #     # set port manually
    #     product_parameters1.parameters['port'].set('3456')
    #
    #     self.assertFalse(product_parameters1.has_all_set())
    #
    #     param_host = product_parameters1.parameters['host']
    #     self.assertTrue(param_host.has_set)
    #     self.assertEqual(product_parameters1['host'], 'host1')
    #
    #     param_port = product_parameters1.parameters['port']
    #     self.assertTrue(param_port.has_set)
    #
    #     param_username = product_parameters1.parameters['username']
    #     self.assertTrue(param_username.has_set)
    #
    #     param_password = product_parameters1.parameters['password']
    #     self.assertFalse(param_password.has_set)
    #
    #
    #     # product 2
    #     install_manager.fill_parameters(product2)
    #     product_parameters2 = product2.get_parameters()
    #
    #     self.assertFalse(product_parameters2.has_all_set())
    #
    #     param_host = product_parameters2.parameters['host']
    #     self.assertTrue(param_host.has_set)
    #     self.assertEqual(product_parameters2['host'], 'host2')
    #
    #     param_port = product_parameters2.parameters['port']
    #     self.assertFalse(param_port.has_set)
    #
    #     param_username = product_parameters2.parameters['username']
    #     self.assertTrue(param_username.has_set)
    #
    #     param_password = product_parameters2.parameters['password']
    #     self.assertFalse(param_password.has_set)



    # def test_manager(self):
    #     parameters_all = ParametersParserStr(self.args_parameters).parameters
    #     orig_im = InstallManager(self.core)
    #     orig_im.add_parameters_args(
    #         (
    #             'prod1@host=host1',
    #             'prod2@host=host2',
    #             'foo=bar',
    #             'prod2@foo=bar2',
    #             'username=root'
    #         )
    #     )
    #     orig_im.add_product(self.core.feed.get_product('Node.js'))
    #     orig_im.add_product(self.core.feed.get_product('Mysql'))
    #
    #     state = orig_im.get_state()
    #
    #     new_im = self.core.create_install_manager_from_state(state)
    #
    #     self.assertEqual(len(new_im.products_to_install), len(orig_im.products))
    #     self.assertEqual(len(new_im.requested_products), len(orig_im.requested_products))
    #     self.assertEqual(len(new_im.parameter_manager.parameters), len(orig_im.parameter_manager.parameters))




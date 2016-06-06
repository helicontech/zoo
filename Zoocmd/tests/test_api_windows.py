# -*- coding: utf-8 -*-

import unittest
from core.core import Core


class WindowsApiTests(unittest.TestCase):

    def runTest(self):
        self.test_registry_read()
        self.test_set_system_env()
        self.test_iis_api()
        self.test_windows_installation_type()

    @classmethod
    def setUpClass(cls):
        cls.core = Core.get_instance()
        cls.registry = cls.core.api.os.registry

    def test_registry_read(self):
        self.assertEqual(
            self.registry.read(r'HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'TEMP'),
            r'%SystemRoot%\TEMP'
        )

    def test_set_system_env(self):
        self.registry.set_system_env('ZOO_TEST_123', '9876543210')
        self.assertEqual(
            self.registry.read(self.registry.ENVS_KEY, 'ZOO_TEST_123'),
            '9876543210'
        )
        self.registry.remove_system_env('ZOO_TEST_123')
        self.assertIsNone(
            self.registry.read(self.registry.ENVS_KEY, 'ZOO_TEST_123'),
        )

    def test_iis_api(self):
        p1 = self.core.expandvars(self.core.api.os.web_server.map_webserver_path('Default Web Site')).lower()
        self.assertEqual(
            p1,
            r'c:\inetpub\wwwroot'
        )

        p2 = self.core.expandvars(self.core.api.os.web_server.map_webserver_path('default web site/')).lower()
        self.assertEqual(
            p2,
            r'c:\inetpub\wwwroot'
        )

    def test_windows_installation_type(self):
        self.assertIn(
            self.core.api.os.registry.get_windows_installation_type(),
            ('Client', 'Server', 'Server Core')
        )

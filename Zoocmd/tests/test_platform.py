# -*- coding: utf-8 -*-

import unittest

from core.models.platform import Platform, PlatformError


class PlatformTests(unittest.TestCase):


    def runTest(self):
        self.test_match()
        self.test_os_version_match()
        self.test_parse()

    def test_match(self):

        self.assertTrue(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows', bitness='32', web_server='iis', lang='en')))
        self.assertTrue(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows', bitness='32', web_server='iis')))
        self.assertTrue(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows', bitness='32')))
        self.assertTrue(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows')))
        self.assertTrue(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform()))

        self.assertFalse(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows', bitness='32', web_server='iis', lang='de')))
        self.assertFalse(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows', bitness='32', web_server='apache', lang='en')))
        self.assertFalse(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='windows', bitness='64', web_server='iis', lang='en')))
        self.assertFalse(
            Platform(os='windows', bitness='32', web_server='iis', lang='en').match(
                Platform(os='ubuntu', bitness='32', web_server='iis', lang='en')))

    def test_parse(self):
        #self.assertRaises(PlatformException, Platform, os='dos')
        self.assertRaises(PlatformError, Platform, bitness='128')
        self.assertRaises(PlatformError, Platform, web_server='mysql')

    def test_os_version_match(self):
        self.assertTrue(Platform(os='windows', os_version='5.0').match(Platform(os='windows', os_version='5.0')))
        self.assertFalse(Platform(os='windows', os_version='5.0').match(Platform(os='windows-core', os_version='5.0')))
        self.assertFalse(Platform(os='windows', os_version='5.0').match(Platform(os='windows', os_version='5.1')))

        self.assertTrue(Platform(os='windows>5.0').match(Platform(os='windows', os_version='5.1')))
        self.assertFalse(Platform(os='windows>5.0').match(Platform(os='windows', os_version='4.9')))

        self.assertTrue(Platform(os='windows', os_version='5.1').match(Platform(os='windows>5.0')))
        self.assertFalse(Platform(os='windows', os_version='4.9').match(Platform(os='windows>5.0')))

        self.assertTrue(Platform(os='windows', os_version='5.1').match(Platform(os='windows>5.0,<5.2')))
        self.assertFalse(Platform(os='windows', os_version='5.2').match(Platform(os='windows>5.0,<5.2')))

"""
Copyright © Helicon Tech. All rights reserved.
"""

import unittest
from new_core import settings_manager

class TestSettingsManager(unittest.TestCase):
    def test_load_settings(self):
        settings=settings_manager.load_settings()
        self.assertIs(type(settings),settings_manager.Settings)
        print(settings)

    def test_save_settings(self):
        settings=settings_manager.load_settings()
        settings_manager.save_settings(settings,settings.root + '/test_settings.yaml')

class TestStringMethods(unittest.TestCase):

  def test_upper(self):
      self.assertEqual('foo'.upper(), 'FOO')

  def test_isupper(self):
      self.assertTrue('FOO'.isupper())
      self.assertFalse('Foo'.isupper())

  def test_split(self):
      s = 'hello world'
      self.assertEqual(s.split(), ['hello', 'world'])
      # check that s.split fails when the separator is not a string
      with self.assertRaises(TypeError):
          s.split(2)

if __name__ == '__main__':
    unittest.main()
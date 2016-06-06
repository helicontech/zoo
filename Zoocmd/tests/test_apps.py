# -*- coding: utf-8 -*-

import unittest

from core.core import Core


class ApplicationLoaderTests(unittest.TestCase):

    def runTest(self):
        self.test_get_state()

    @classmethod
    def setUpClass(cls):
        cls.core = Core.get_instance()
        cls.core.feed.raw_collection.append(dict(application='app1', title='App1'))
        cls.core.feed.raw_collection.append(dict(application='app2', title='App2'))

    def test_get_state(self):
        app = self.core.feed.get_product('app1')
        state = app.to_dict()
        self.assertIn('application', state)
        self.assertNotIn('product', state)
        self.assertEqual(state.get('application'), 'app1')
        self.assertEqual(state.get('title'), 'App1')

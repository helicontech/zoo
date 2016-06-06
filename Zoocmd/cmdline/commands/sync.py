# -*- coding: utf-8 -*-


class SyncCommand(object):
    """
    Helper class to call core sync
    """

    def __init__(self, core):
        self.core = core

    def do(self):
        """
        Do core sync
        """
        self.core.sync()


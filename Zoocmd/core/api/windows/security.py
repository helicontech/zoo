# -*- coding: utf-8 -*-


class SecurityApi(object):
    """
    Api for security actions
    """

    def __init__(self, core):
        self.core = core

    def set_write_permission(self, path, user_or_group):
        """
        Sets write permission on path for user_or_group via icacls.exe utility
        :return:
        """
        cmd = r'%SystemRoot%\System32\icacls "{0}" /grant {1}:(OI)(CI)F'.format(path, user_or_group)
        self.core.api.os.shell.cmd(cmd)



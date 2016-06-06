# -*- coding: utf-8 -*-


class InstalledProductInfo(object):
    """
    Represents information about instaled products.
    It is result of find_installed_command.
    """
    def __init__(self):
        self.name = ""
        self.version = ""
        self.guid = ""
        self.uninstall_string = ""
        self.bitness = ""
        self.install_dir = ""

    def __lt__(self, other):
        """
        Special function that implements '>' operation.
        """
        return self.name < other.name

    def __str__(self):
        return "InstalledProduct('{0}', '{1}', '{2}')".format(self.name, self.version, self.install_dir)
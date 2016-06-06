# -*- coding: utf-8 -*-
import os


class WindowsApi(object):
    """
    Implements Windows api for using in install_command for product.
    Instance with name 'windows' is available in install_commands.
    WindowsApi is wrapper for:
    - core.api.windows.feature
    - core.api.windows.msi_manager
    - core.api.windows.feature
    - core.api.windows.security
    WindowsApi knows installing product and expands env variables in arguments.
    Example:
    windows.install_msi(...)
    """

    def __init__(self, core, product):
        self.core = core
        self.product = product

    def registry_read(self, path, name, bitness=None):
        """
        Reads and returns value from registry.
        """
        path = self.core.expandvars(path, self.product)
        name = self.core.expandvars(name, self.product)
        if bitness is None:
            bitness = self.core.platform.bitness
        return self.core.api.os.registry.read(path, name, bitness)

    def registry_write(self, path, name, value, bitness=None):
        """
        Writes to registry.
        """
        path = self.core.expandvars(path, self.product)
        name = self.core.expandvars(name, self.product)
        if bitness is None:
            bitness = self.core.platform.bitness
        return self.core.api.os.registry.write(path, name, value, bitness)

    def registry_delete(self, path, bitness=None):
        """
        Writes to registry.
        """
        path = self.core.expandvars(path, self.product)
        if bitness is None:
            bitness = self.core.platform.bitness
        return self.core.api.os.registry.delete(path, bitness)

    def install_msi(self, msi_path, optional_parameters: dict=None, ignore_exit_code=False, no_wait=False):
        """
        Install MSI installer
        :param msi_path: path to msi file
        :param optional_parameters: parameters passed to installer
        :param ignore_exit_code:
        :param no_wait:
        :return:
        """
        msi_path = self.core.expandvars(msi_path, self.product)
        msi_file = os.path.basename(msi_path)
        log_path = os.path.join(self.core.log_manager.get_log_dir(), '{0}_msi.log'.format(msi_file))
        # TODO add generate path for log_path
        return self.core.api.os.msi.install(
            msi_path,
            log_path,
            optional_parameters=optional_parameters,
            ignore_exit_code=ignore_exit_code,
            no_wait=no_wait
        )

    def uninstall_msi(self, msi_path, ignore_exit_code=False):
        """
        Uninstalls MSI installer.
        """
        msi_path = self.core.expandvars(msi_path, self.product)
        msi_file = os.path.basename(msi_path)
        log_path = os.path.join(self.core.log_manager.get_log_dir(), '{0}_msi.log'.format(msi_file))
        return self.core.api.os.msi.uninstall(msi_path, log_path, ignore_exit_code=ignore_exit_code)

    def uninstall_msi_by_name(self, name, version=None, ignore_exit_code=False):
        """
        Searches MSI guid in registry by name and uninstalls program with this guid.
        Used in uninstall_command.
        :param name: program name EITHER STRING OR REGULAR EXPRESSION
        :param version: program version to uninstall
        :return:
        """
        program = self.get_installed_program(name, version)
        if program is None:
            raise Exception("Can't find program '{0}({1})'".format(name, version))
        log_path = os.path.join(self.core.log_manager.get_log_dir(), '{0}_msi.log'.format(program.name))
        return self.core.api.os.msi.uninstall_program(program, log_path, version=version, ignore_exit_code=ignore_exit_code)

    def get_installed_program(self, name, version=None):
        """
        Returns info about installed program.
        Used in find_installed_command.
        """
        return self.core.api.os.registry.get_installed_program(name, version)

    def install_feature(self, name):
        """
        Installs Windows feature ny name (IIS, .Net, ...).
        Used in .NetFramework and IIS install_command.
        """
        self.core.api.os.feature.install(name)

    def uninstall_feature(self, name):
        """
        Uninstalls Windows feature ny name (IIS, .Net, ...).
        Used in .NetFramework and IIS uninstall_command.
        """
        self.core.api.os.feature.uninstall(name)

    def get_installation_type(self):
        """
        Returns Windows installation type: Server Core, Server or Desktop.
        Used in NetFramework install_command.
        """
        self.core.api.os.registry.get_windows_installation_type()

    def set_write_permission(self, path, user_or_group):
        """
        Set write permission of 'path' for 'user_or_group'.
        Used for install_command in zoo apps.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.security.set_write_permission(path, user_or_group)

    def get_file_version(self, filename, parts=None):
        """
        Returns version of windows executable file.
        Used in find_installed_command to get version.
        """
        filename = self.core.expandvars(filename, self.product)
        return self.core.api.os.shell.get_file_version(filename, parts)

    def add_to_system_path(self, path):
        """
        Adds path to system PATH env variable.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.registry.add_to_system_path(path)

    def remove_from_system_path(self, path):
        """
        Removes path from system PATH env variable.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.registry.remove_from_system_path(path)

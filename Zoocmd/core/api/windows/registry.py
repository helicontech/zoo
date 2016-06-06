# encoding: utf-8

import logging
import re
import winreg

from core.models.installed_product import InstalledProductInfo
from core.version_comparer import VersionComparer


class Registry(object):
    """
    Windows registry API
    """

    ENVS_KEY = r'HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
    CURR_VERSION_KEY = r'HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion'

    def read(self, key, name, bitness=None):
        """
        Read value by name in key
        :param key: registry key
        :param name: value name
        :param bitness: 32 or 64
        """
        hive, key = self._get_registry_hive(key)
        bitness_flag = Registry._get_bitness_flag(bitness)
        conn = winreg.ConnectRegistry(None, hive)
        try:
            reg_key = winreg.OpenKey(conn, key, 0, winreg.KEY_READ | bitness_flag)
            val, _ = winreg.QueryValueEx(reg_key, name)
        except FileNotFoundError:
            # name not found
            return None

        return val

    def write(self, key, name, value, bitness=None):
        """
        Writes value to registry
        :param key: registry key
        :param name: value name
        :param value:
        :param bitness:
        :return:
        """
        logging.debug('{0} {1}:{2}'.format(key, name, value))
        hive, path = self._get_registry_hive(key)
        bitness_flag = Registry._get_bitness_flag(bitness)
        # conn = winreg.ConnectRegistry(None, hive)
        # reg_key = winreg.OpenKey(conn, path, 0, winreg.KEY_WRITE | bitness_flag)
        with winreg.CreateKeyEx(hive, path, 0, winreg.KEY_WRITE | bitness_flag) as reg_key:
            winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, value)

    def delete(self, key, bitness=None):
        """
        Deletes key registry
        :param key: registry key
        :param bitness:
        """
        logging.debug('{0}'.format(key))
        hive, path = self._get_registry_hive(key)
        bitness_flag = Registry._get_bitness_flag(bitness)
        winreg.DeleteKeyEx(hive, path, bitness_flag, 0)

    def get_system_env(self, name):
        """
        Returns system env variable from registry.
        :param name: env name
        :return: env value
        """
        return self.read(self.ENVS_KEY, name)

    def set_system_env(self, name, value):
        """
        Write system env variable to registry.
        :param name:
        :param value:
        :return:
        """
        self.write(self.ENVS_KEY, name, value)

    def remove_system_env(self, name):
        """
        Remove system env variable from registry.
        :param name:
        :return:
        """
        logging.debug(name)
        hive, path = self._get_registry_hive(self.ENVS_KEY)
        conn = winreg.ConnectRegistry(None, hive)
        reg_key = winreg.OpenKey(conn, path, 0, winreg.KEY_WRITE)
        try:
            winreg.DeleteValue(reg_key, name)
        except FileNotFoundError:
            # name not found
            pass

    @staticmethod
    def _get_registry_hive(path):
        """
        Returns registry branch for path
        :param path: registry path
        :return:
        """
        hive = winreg.HKEY_LOCAL_MACHINE
        if path.startswith("HKLM"):
            hive = winreg.HKEY_LOCAL_MACHINE
            path = path[5:]
        if path.startswith("HKCU"):
            hive = winreg.HKEY_CURRENT_USER
            path = path[5:]
        if path.startswith("HKCR"):
            hive = winreg.HKEY_CLASSES_ROOT
            path = path[5:]

        return hive, path

    @staticmethod
    def _lower_if_possible(x):
        try:
            return x.lower()
        except AttributeError:
            return x

    @staticmethod
    def _get_bitness_flag(bitness):
        if bitness in (32, "32"):
            return winreg.KEY_WOW64_32KEY
        if bitness in (64, "64"):
            return winreg.KEY_WOW64_64KEY
        return 0

    def get_installed_programs(self, bitness="all"):
        """
        Search installed programs in registry with specified bitness
        :param bitness:
        :return: list of installed programs
        """
        programs = []
        if bitness == "all":
            programs.extend(self._get_installed_programs_on_windows_ex(winreg.KEY_READ))
            programs.extend(self._get_installed_programs_on_windows_ex(winreg.KEY_READ | winreg.KEY_WOW64_64KEY))

        if bitness == "32":
            programs.extend(self._get_installed_programs_on_windows_ex(winreg.KEY_READ))

        if bitness == "64":
            programs.extend(self._get_installed_programs_on_windows_ex(winreg.KEY_READ | winreg.KEY_WOW64_64KEY))

        programs.sort(key=lambda x: self._lower_if_possible(x))
        return programs

    @staticmethod
    def _get_installed_programs_on_windows_ex(mode):
        """
        Helper to search installed programs in system-wide and user scope
        :param mode:
        :return:
        """
        programs = []
        programs.extend(Registry._get_installed_programs_on_windows_ex2(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", mode))
        programs.extend(Registry._get_installed_programs_on_windows_ex2(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", mode))
        return programs

    @staticmethod
    def _get_installed_programs_on_windows_ex2(key, subkey, mode):
        """
        Internal implementation of searching programs in registry
        :param key:
        :param subkey:
        :param mode:
        :return:
        """
        programs = []
        try:
            conn = winreg.ConnectRegistry(None, key)
            reg_key = winreg.OpenKey(conn, subkey, 0, mode)
            i = -1

            bitness = "x86"
            if mode & winreg.KEY_WOW64_64KEY:
                bitness = "x64"
            while True:
                try:
                    i += 1
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)
                    val, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    display_version, _ = winreg.QueryValueEx(subkey, "DisplayVersion")
                    uninstall_string, _ = winreg.QueryValueEx(subkey, "UninstallString")
                    install_location, _ = winreg.QueryValueEx(subkey, "InstallLocation")

                    pr = InstalledProductInfo()
                    pr.name = val
                    pr.version= display_version
                    pr.guid = subkey_name
                    pr.uninstall_string = uninstall_string
                    pr.bitness = bitness
                    pr.install_dir = install_location
                    programs.append(pr)

                except WindowsError as e:
                    if e.winerror == 259:
                        break
                    continue
        except Exception as ex:
            pass

        return programs

    def get_installed_program(self, name, version=None):
        """
        Search program in installed program list by name
        :param name:
        :param version:
        :return:
        """
        for program in self.get_installed_programs():
            if isinstance(name, re._pattern_type):
                if name.match(program.name.lower()):
                    if version:
                        if VersionComparer('==', version).match(program.version):
                            return program
                    else:
                        return program
            else:
                if name.lower() == program.name.lower():
                    return program

        return None

    def get_windows_installation_type(self):
        """
        Returns windows intallation type
        """
        return self.read(self.CURR_VERSION_KEY, 'InstallationType')

    def _is_in_system_path(self, folder):
        """
        Checks that folder in system PATH env variable
        """
        folder = folder.lower().strip()
        path_str = self.read(self.ENVS_KEY, 'PATH')
        for part in path_str.split(';'):
            if folder == part.lower().strip():
                return True
        return False

    def add_to_system_path(self, folder):
        """
        Adds folder to system PATH env variable
        """
        logging.debug(folder)
        if not self._is_in_system_path(folder):
            path_str = self.read(self.ENVS_KEY, 'PATH')
            path_str = '{0};{1}'.format(folder, path_str)
            self.write(self.ENVS_KEY, 'PATH', path_str)

    def remove_from_system_path(self, folder):
        """
        Removes folder from system PATH env variable
        :param folder:
        :return:
        """
        logging.debug(folder)
        if self._is_in_system_path(folder):
            folder = folder.lower().strip()
            path_str = self.read(self.ENVS_KEY, 'PATH')
            new_parts = []
            # split path by ';'
            for part in path_str.split(';'):
                if folder != part.lower().strip():
                    new_parts.append(part)
            new_path_str = ';'.join(new_parts)
            self.write(self.ENVS_KEY, 'PATH', new_path_str)
        else:
            logging.debug('{0} not found in PATH'.format(folder))

    def get_system_path(self):
        """
        Returns system PATH variable
        :return:
        """
        return self.read(self.ENVS_KEY, 'PATH')

from core.core import Core
import logging
import os
import win32api


class MsiManager(object):
    """
    Api to install or uninstall MSI
    """

    @staticmethod
    def install(filename, log_path, optional_parameters: dict=None, ignore_exit_code=False, no_wait=False):
        """
        Install MSI with options
        :param filename:
        :param log_path:
        :param optional_parameters:
        :param ignore_exit_code:
        :param no_wait:
        """
        command = r'msiexec.exe /norestart /q /i "{0}" /l! "{1}" ALLUSERS=1'.format(filename, log_path)
        if optional_parameters:
            for k, v in optional_parameters.items():
                if v and v != "":
                    command += ' {0}="{1}"'.format(k, v)

        exit_code = Core.get_instance().api.os.shell.cmd(command, ignore_exit_code=True, no_wait=no_wait)
        if exit_code == 3010: # Reboot required code
            logging.warning('WARNING: Installation requested a system reboot.\nYou may need to reboot the system manually to complete this installation.')
        elif exit_code != 0 and not ignore_exit_code:
            # Other errors rise exception
            raise RuntimeError('Installation "{0}" failed: ({1}) {2}'.format(filename, exit_code, win32api.FormatMessageW(exit_code)))
        return exit_code

    @staticmethod
    def uninstall(filename, log_path, ignore_exit_code=False, no_wait=False):
        """
        Uninstall MSI with options
        :param filename:
        :param log_path:
        :param ignore_exit_code:
        :return:
        """
        command = r'msiexec.exe /norestart /q /X "{0}" /l! "{1}"'.format(filename, log_path)
        exit_code = Core.get_instance().api.os.shell.cmd(command, ignore_exit_code=True, no_wait=no_wait)
        if exit_code == 3010: # Reboot required code
            logging.warning('WARNING: Installation requested a system reboot.\nYou may need to reboot the system manually to complete this installation.')
        elif exit_code != 0 and not ignore_exit_code:
            # Other errors rise exception
            raise RuntimeError('Installation "{0}" failed: ({1}) {2}'.format(filename, exit_code, win32api.FormatMessageW(exit_code)))
        return exit_code

    @staticmethod
    def uninstall_program(program, log_path, version=None, ignore_exit_code=False, no_wait=False):
        """
        Uninstall MSI by program name
        :param program: object of type InstalledProductInfo()
        :param version: program version to uninstall
        :param log_path:
        :param ignore_exit_code:
        :return:
        """
        if program.guid is None:
            raise Exception("Can't uninstall program. No program.guid.")
        command = r'msiexec.exe /norestart /q /X{0} /l! "{1}"'.format(program.guid, log_path)
        exit_code = Core.get_instance().api.os.shell.cmd(command, ignore_exit_code=True, no_wait=no_wait)
        if exit_code == 3010: # Reboot required code
            logging.warning('WARNING: Installation requested a system reboot.\nYou may need to reboot the system manually to complete this installation.')
        elif exit_code != 0 and not ignore_exit_code:
            # Other errors rise exception
            raise RuntimeError('Installation "{0}" failed: ({1}) {2}'.format(program.name, exit_code, win32api.FormatMessageW(exit_code)))
        return exit_code

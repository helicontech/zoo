# -*- coding: utf-8 -*-

import os
import logging
import shutil
import re
import sys
import subprocess
import win32api
import platform
# import shlex


class WindowsShell(object):
    """
    Windows shell api: executing command, handling files and folder, extracting archives.
    """

    ROOT = ''

    def __init__(self, root):
        WindowsShell.ROOT = root


    # @staticmethod
    # def execute(command, ignore_exit_code=False, envs=None, no_wait=False):
    #     """
    #     Run command via subprocess and return exit code
    #     """
    #     logging.info('> {0}'.format(command))
    #
    #     process = subprocess.Popen(command, env=envs)
    #
    #     # exit if do not need to wait process
    #     if no_wait:
    #         return 0
    #
    #     process.wait()
    #     exit_code = process.returncode
    #
    #     if exit_code != 0 and not ignore_exit_code:
    #         # raise error if exit code is not 0
    #         raise RuntimeError('Execute of command "{0}" failed with status {1}'.format(command, exit_code))
    #
    #     return exit_code


    @staticmethod
    def cmd(command, ignore_exit_code=False, envs=None, no_wait=False):
        """
        Run command via subprocess and return exit code
        """
        logging.info('> {0}'.format(command))

        # This code is needed to start 64-bit version of cmd.exe on 64-bit os.
        # Not sure yet which version is correct
        if platform.machine().endswith('64'):
            executable = '{0}\Sysnative\cmd.exe /C "{1}"'.format(os.getenv('SystemRoot'), command)
        else:
            executable = '{0}\System32\cmd.exe /C "{1}"'.format(os.getenv('SystemRoot'), command)

        # exit_code = subprocess.check_call(executable, env=envs, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        process = subprocess.Popen(executable, env=envs, shell=True, stdout=sys.stdout, stderr=sys.stderr)

        # exit if do not need to wait process
        if no_wait:
            return 0

        process.wait()
        exit_code = process.returncode
        if exit_code != 0 and not ignore_exit_code:
            try:
                str_error = os.strerror(exit_code)
            except (OverflowError, ValueError):
                str_error = ""
            # raise error if exit code is not 0
            raise RuntimeError('Execute of command "{0}" failed: ({1}) {2}'.format(command, exit_code, str_error ))

        return exit_code

    @staticmethod
    def get_cmd_output(command):
        """
        Executes command and return output
        """
        logging.debug(command)
        return subprocess.check_output(command)

    @staticmethod
    def un7zip(source_filename, target_dir, source_internal_dir=None, delete: bool=False):
        """
        Unzip file to target_dir.
        :param source_filename: source arhcive file (.zip or .7z)
        :param target_dir: dir to extract
        :param source_internal_dir: directory in archive to extract
        :param delete: delete or not archive after extract
        :param log_path: log file name
        """
        WindowsShell.cmd('"{0}" x "{1}" {2} "-o{3}" -y'.format(
            os.path.join(WindowsShell.ROOT, r'7za.exe'),
            source_filename, source_internal_dir or '', target_dir))

        if source_internal_dir:
            WindowsShell.move_dir(os.path.join(target_dir, source_internal_dir), target_dir)

        if delete:
            WindowsShell.delete_path(source_filename)

    @staticmethod
    def move_dir(src, dest):
        """
        Move 'src' directory to 'dest'.
        """
        WindowsShell.cmd(r'xcopy "{0}" "{1}" /S /E /Y'.format(src, dest))
        WindowsShell.delete_path(src)

    @staticmethod
    def ensure_exists(source_filename):
        """
        Raises error if source_filename is not exist.
        """
        return os.path.isfile(source_filename)

    # i think such functions are not depends to this module
    @staticmethod
    def delete_path(path):
        """
        Deletes file ot folder specified in path. Ignores any errors.
        :param path: file or folder
        """
        logging.info("Deleting path '%s'", path)

        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)

    @staticmethod
    def get_file_version(filename, parts=None):
        """
        Returns version of win-executable file.
        :param filename:
        :param parts: Number of version parts to return
        """
        logging.debug(filename)
        try:
            info = win32api.GetFileVersionInfo(filename, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            if parts == 1:
                return "{0}".format(win32api.HIWORD(ms))
            if parts == 2:
                return "{0}.{1}".format(win32api.HIWORD(ms), win32api.LOWORD(ms))
            if parts == 3:
                return "{0}.{1}.{2}".format(win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls))

            return "{0}.{1}.{2}.{3}".format(win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
        except Exception:
            return None

    @staticmethod
    def chdir(path):
        """
        Changes current directory.
        """
        logging.debug(path)
        os.chdir(path)

    @staticmethod
    def replace_in_file(path, pattern, replace):
        """
        Replaces text in file.
        :param path: physical path to file
        :param pattern: text or regexp to search
        :param replace: text to replace
        """
        #logging.info("patch file '{0}': '{1}' -> '{2}'".format(filename, pattern, replace))

        WindowsShell.ensure_exists(path)

        with open(path, 'r') as f:
            s = f.read()
        (new_string, number_of_subs_made) = re.subn(pattern, replace, s, count=0, flags=re.M | re.I | re.U)
        s = new_string
        with open(path, 'w') as f:
            f.write(s)

        logging.debug('file {0} patched'.format(path))

    @staticmethod
    def add_to_path(path):
        """
        Adds 'path' to PATH env variable of current process.
        """
        logging.debug(path)
        WindowsShell.remove_from_path(path)
        os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

    @staticmethod
    def remove_from_path(path):
        """
        Removes path from PATH env variable of current process
        :param path:
        """
        logging.debug(path)
        system_path = os.environ["PATH"]
        # split PATH
        paths = system_path.split(os.pathsep)
        for part in paths:
            if part.lower() == path.lower():
                paths.remove(part)
        system_path = os.pathsep.join(paths)
        os.environ["PATH"] = system_path

    @staticmethod
    def copy_file(source, destination):
        """
        Copies 'source' file to 'destination'
        """
        shutil.copy(source, destination)

    @staticmethod
    def append_file_str(string: str, destination):
        """
        Appends content of string to  'destination' file.
        """

        if not os.path.exists(destination):
            raise FileNotFoundError(destination)
        with open(destination, 'a+b') as df:
                df.write(bytes(string, 'UTF-8'))

    @staticmethod
    def append_file(source, destination):
        """
        Appends content of 'source' file to 'destination' file.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(source)
        if not os.path.exists(destination):
            raise FileNotFoundError(destination)
        with open(destination, 'a+b') as df:
            with open(source, 'rb') as sf:
                df.write(sf.read())

    @staticmethod
    def make_dir(path):
        """
        Makes directories tree specified in 'path'.
        """
        os.makedirs(path, exist_ok=True)

    # DEPRECATED
    @staticmethod
    def is_alive(pid):
        """
            check existed process
        """
        out = subprocess.check_output(["tasklist", "/fi", "PID eq %i" % pid]).strip()
        if out == b'INFO: No tasks are running which match the specified criteria.':
            return False
        return True

        # try:
        #     os.kill(pid, 0)
        #     return True
        # except OSError:
        #     return False

    @staticmethod
    def dir_list_file(path):
        """
        Return the list of files in giving directory and subdirectories
        """
        total_size = 0
        list_flnames = []
        for dir_path, dir_names, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dir_path, f)
                list_flnames.append(fp)
        return list_flnames

    @staticmethod
    def dir_size(path):
        """
        Return directory size in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    @staticmethod
    def get_short_path_name(long_name):
        """
        Return short name of specified file name.
        """
        return win32api.GetShortPathName(long_name)

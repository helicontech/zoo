# -*- coding: utf-8 -*-
import os
import shutil

class OsApi(object):
    """
    Implements OS api for using in install_command for product.
    Instance with name 'os' is available in install_commands.
    OsApi is wrapper for core.api.windows.shell.WindowsShell.
    OsApi knows installing product and expands env variables in arguments.
    Example:
    os.cmd(...)
    os.chdir(...)
    """

    def __init__(self, core, product):
        self.core = core
        self.product = product
        self.log_dir = None

    def cmd(self, command, ignore_exit_code=False):
        """
        Executes command.
        """
        """
        List attributes (currently not allowed)
        if hasattr(command, '__iter__'):
            command = [self.core.expandvars(item, product=self.product) for item in command]
        else:
            command = self.core.expandvars(command, product=self.product)
        """
        command = self.core.expandvars(command, product=self.product)
        self.core.api.os.shell.cmd(command, ignore_exit_code=ignore_exit_code)

    def delete_path(self, path, ignore_errors=True):
        """
        Deletes path.
        """
        path = self.core.expandvars(path, self.product)
        """
        Deletes file ot folder specified in path. Ignores any errors.
        :param path: file or folder
        """
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=ignore_errors)
        elif os.path.isfile(path):
            os.remove(path)

    def movetree(self, source_dir, dest):
        """
            move tree of the directory excluding the name of directory to another directory
        """
        names = os.listdir(source_dir)
        for i in names:
            copy_item = os.path.join(source_dir,i)
            shutil.move(copy_item, source_dir)

    def move(self, source, dest):
        shutil.move(source, dest)

    def copytree(self, src, dst):
        shutil.copytree(src, dst, symlinks=False, ignore=None)

    def copy_file(self, source, dest):
        """
        Copies 'source' file to 'dest'.
        :param source:
        :param dest:
        :return:
        """
        source = self.core.expandvars(source, self.product)
        dest = self.core.expandvars(dest, self.product)
        self.core.api.os.shell.copy_file(source, dest)

    def append_file(self, source, dest):
        """
        Append content of 'source' file to 'dest'.
        """
        source = self.core.expandvars(source, self.product)
        dest = self.core.expandvars(dest, self.product)
        self.core.api.os.shell.append_file(source, dest)

    def append_file_str(self, some_string: str, dest):
        """
        Append content of 'source' file to 'dest'.
        """
        dest = self.core.expandvars(dest, self.product)
        self.core.api.os.shell.append_file_str(some_string, dest)

    def un7zip(self, path, destination, source_internal_dir=None):
        """
        Extracts archive to 'destination' directory.
        :param path:
        :param destination:
        :param source_internal_dir: dir in archive to extract.
        """
        if not path:
            raise Exception("path does not specified %s" % path)
        if not destination:
            raise Exception("destination does not specified %s" % destination)

        path = self.core.expandvars(path, self.product)
        destination = self.core.expandvars(destination, self.product)
        self.core.api.os.shell.un7zip(path, destination, source_internal_dir, delete=False)

    def setup_log_dir(self):
        self.log_dir = self.core.log_manager.get_log_dir()
        # HOTFIX TODO avoid of this
        os.environ["LOG_DIR"] = self.log_dir

    def get_system_env(self, name):
        return self.core.api.os.registry.get_system_env(name)

    def set_system_env(self, name, value):
        self.core.api.os.registry.set_system_env(name, value)

    def remove_system_env(self, name):
        self.core.api.os.registry.remove_system_env(name)

    def chdir(self, path):
        """
        Changes current directory.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.shell.chdir(path)

    def make_dir(self, path):
        """
        Makes directories specified in 'path' if not exists.
        """
        path = self.core.expandvars(path, self.product)
        self.core.api.os.shell.make_dir(path)

    def path_exists(self, path)-> bool:
        """
        Check path exists.
        """
        path = self.core.expandvars(path, self.product)
        return os.path.exists(path)

    def path_join(self, *paths):
        """
        Joins list of paths into single string.
        """
        return os.path.join(*[self.core.expandvars(path, self.product) for path in paths])

    def read_file(self, path):
        """
        Returns file content.
        """
        path = self.core.expandvars(path, self.product)
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read()
        except:
            pass
        return None

    def replace_in_file(self, path, pattern, replace):
        """
        Replaces text in file specified in 'path' with 'pattern' to 'replace'.
        :param path:
        :param pattern: text or regexp object to search
        :param replace:
        :return:
        """
        path = self.core.expandvars(path, self.product)
        return self.core.api.os.shell.replace_in_file(path, pattern, replace)
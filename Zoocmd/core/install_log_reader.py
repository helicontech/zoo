# -*- coding: utf-8 -*-

import os
import os.path
import datetime
import sys
import logging
from core.core import Core

# DEPRECATED
class InstallLogReader(object):
    """
     Создает директорию для логов атомарной таски,
     запоминает ее состояние
     выдает измненеия с прошлой позиции
    """


    def __init__(self, *kargs, **kargws):
        self.path = kargws["path"]
        self.task_id = kargws["task_id"]
        self.working_path = InstallLogReader.generate_path_name(self.path, self.task_id)
        self.watching_list = {}
        self.last_modified = None
        self.core = Core.get_instance()
        if not self.core.api.os.shell.ensure_exists(self.working_path):
            self.core.api.os.shell.make_dir(self.working_path)


    """
        return  common log name for executable command
    """
    def common_working_log(self):

        if sys.platform == "win32":
            return self.working_path + "\\common.log"
        else:
            return self.working_path + "/common.log"

    """
        Is the directory has been changed
        then there are new files in it
    """
    # TODO merge with log manager

    def is_changed(self):
        change_time = os.path.getmtime(self.working_path)

        if self.last_modified != change_time:
            return True
        return False

    # read new lines from files
    def read_new(self):
        lines = []
        for k in self.watching_list.keys():
            file_handle = self.watching_list[k]
            line = file_handle.readlines()
            for one_item in line:
                lines.append(one_item)

        return lines

    """
        read the directory
        and update the watch list of files
    """

    def update_list_checking_files(self):
            for item in self.core.api.os.shell.dir_list_file(self.working_path):
                change_time = os.path.getmtime(self.working_path)
                self.last_modified = change_time
                if item not in self.watching_list:
                    file_handle = open(item, 'r')
                    self.watching_list[item] = file_handle

    """
     remove all log files from directory
    """
    def clean_all(self):
            logging.debug(self.watching_list)
            for k in self.watching_list.keys():
                file_handle = self.watching_list[k]
                file_handle.close()

            self.core.api.os.shell.delete_path(self.working_path)


            return self.watching_list

    """
        static method, that generates directory name
    """
    @staticmethod
    def generate_path_name(path, task_id):
        return os.path.join(path, ('task_log' + str(task_id)))

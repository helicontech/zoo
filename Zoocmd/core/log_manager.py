# -*- coding: utf-8 -*-

import os
import os.path
import datetime
import logging

class LogManager(object):
    """
    Хелпер, который cоздает  директории и файлы для логов инсталляций.
    Эти логи случаются во время инсталляции, апгрейда, деинсталляции.
    Получает полный путь с учетом zoo_home, имени продукта, даты
    """
    def __init__(self, core):
        self.core = core
        self.root = self.core.settings.logs_path
        self.watching_list = {}
        self.watching_enc_list = {}
        self.lines_buffer = []
        self.last_modified = None
        self.working_path = None
        self.current_job = None


    def setup_log(self, job_id: int):
        self.working_path = LogManager.generate_path_name(self.root, job_id)
        self.current_job = job_id
        if not self.core.api.os.shell.ensure_exists(self.working_path):
            self.core.api.os.shell.make_dir(self.working_path)





    def get_log_dir(self):
        """
        Возвращает директорию лого для task-ы, создайт ее, если она не существует.
        """
        dir_path = self.working_path
        os.makedirs(dir_path, exist_ok=True)

        return dir_path

    """
        return  common log name for executable command
    """
    def common_working_log(self):
        return os.path.join(self.root, "task%i.log" % self.current_job)


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
            encoding_watch = self.watching_enc_list[k]
            for one_item in line:
                one_item = one_item.decode(encoding="utf8", errors="ignore")
                # not very good design]
                # remove empty strings for msi
                if encoding_watch == "msi":
                    one_item = one_item.replace("\x00", "")
                lines.append(one_item)

        return lines

    """
        read the directory
        and update the watch list of files
    """

    def update_list_checking_files(self, name=None):
            if name is None:

                for item in self.core.api.os.shell.dir_list_file(self.working_path):
                    change_time = os.path.getmtime(self.working_path)
                    self.last_modified = change_time
                    if item not in self.watching_list:
                        file_handle = open(item, 'rb', )
                        self.watching_list[item] = file_handle
                        if item.endswith("_msi.log"):
                            self.watching_enc_list[item] = "msi" #"ucs-2"
                        else:
                            self.watching_enc_list[item] = "utf8"

            else:
                new_name = os.path.join(self.working_path, name)
                if new_name not in self.watching_list:
                    file_handle = open(new_name, 'rb')
                    self.watching_list[new_name] = file_handle
                    if new_name.endswith("_msi.log"):
                        self.watching_enc_list[new_name] = "msi"
                    else:
                        self.watching_enc_list[new_name] = "utf8"





    """
     remove all log files from directory
    """
    def clean_all(self):
            logging.debug(self.watching_list)
            for k in self.watching_list.keys():
                file_handle = self.watching_list[k]
                file_handle.close()
                self.core.api.os.shell.delete_path(k)
            logging.debug("delete logging directory %s" % self.working_path)
            self.core.api.os.shell.delete_path(self.working_path)
            self.core.api.os.shell.delete_path(self.common_working_log())

            return True

    def free(self):
        self.watching_list = {}
        self.watching_enc_list = {}
        self.working_path = None
        self.last_modified = None
        self.current_job = None
        return True

    """
        static method, that generates directory name
    """
    @staticmethod
    def generate_path_name(path, task_id):

        return os.path.join(path, "task_log" + str(task_id))


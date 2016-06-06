# -*- coding: utf-8 -*-

import logging

# deprecated
class TaskDbLogHandler(logging.Handler):
    """
    Хендлер к модулю logging
    чтобы все что пишется в лог попадало в базу данных
    """
    def __init__(self, task_object):
        logging.Handler.__init__(self)
        self.level = logging.DEBUG
        self.task_object = task_object
        self.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s'))

    def emit(self, record):
        if self.task_object:
            self.task_object.add_log(record)

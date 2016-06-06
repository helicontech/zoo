# -*- coding: utf-8 -*-

class LogMessage(object):
    """
      simple log message
      using for communicate
    """
    def __init__(self, *args, **kwargs):
        self.job_state = kwargs["job_state"]
        self.message = kwargs["message"]
        self.job = kwargs["job"]
        self.task_id = kwargs["task_id"]
        self.title = kwargs["title"]
        self.task_state = kwargs["task_state"]

    def __repr__(self):
        return ",".join(["LogMessage", self.job_state, self.message, self.title, str(self.task_id), self.task_state])
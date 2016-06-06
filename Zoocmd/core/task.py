# -*- coding: utf-8 -*-
from core.models.database import TaskPeewee as Task
from core.models.database import JobPeewee  as Job

from core.log_message import LogMessage

import time
import subprocess
import logging
import sys

class Task(object):

    def __init__(self, *agrs, **kwargs):
        self.jobs = kwargs.get("jobs", None)
        if self.jobs is None:
            jobs = Job.select().where(Job.task == self.id,
                                      Job.status == Job.STATUS_PENDING)
            self.jobs = []

            for i in jobs:
                self.jobs.append(i)

        self.data_model = kwargs["task_model"]
        self.id = kwargs["task_model"].id
        self.status = Job.STATUS_PENDING
        self.settings = self.data_model.settings

    def get_status(self):
        return self.status

    def update(self, status=None):
        self.status = status
        if status == Job.STATUS_DONE:
            self.data_model.status = Job.STATUS_DONE
            self.data_model.save()
            return True

        if status == Job.STATUS_RUNNING:
            self.data_model.status = Job.STATUS_RUNNING
            self.data_model.save()
            return True

        if status == Job.STATUS_PENDING:
            self.data_model.status = Job.STATUS_PENDING
            self.data_model.save()
            return True

        if status == Job.STATUS_CANCELED:
            self.data_model.status = Job.STATUS_CANCELED
            jobs = Job.select().where(Job.task == self.id)

            for i in jobs:
                if i.status == Job.STATUS_CANCELED:
                    continue
                # we do not interrupt the running job
                # if i.status == Job.STATUS_RUNNING:
                #     i.status = Job.STATUS_CANCELED
                if i.status == Job.STATUS_EXCEPTION:
                    i.status = Job.STATUS_FAILED
                if i.status == Job.STATUS_PENDING:
                    i.status = Job.STATUS_CANCELED
                i.save()

            self.data_model.save()
            return True

        if status == Job.STATUS_FAILED:
            self.data_model.status = Job.STATUS_FAILED
            jobs = Job.select().where(Job.task == self.id)

            for i in jobs:
                if i.status == Job.STATUS_CANCELED :
                    continue
                # cause we do not call this method if job is running
                # TODO think about of checking process pid
                if i.status == Job.STATUS_RUNNING:
                    i.status = Job.STATUS_FAILED
                if i.status == Job.STATUS_EXCEPTION:
                    i.status = Job.STATUS_FAILED
                if i.status == Job.STATUS_PENDING:
                    i.status = Job.STATUS_CANCELED

                i.save()

            self.data_model.save()
            return True



        return False




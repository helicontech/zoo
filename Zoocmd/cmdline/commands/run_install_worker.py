# -*- coding: utf-8 -*-

import os
import sys
import logging
import time
import traceback
from core.helpers.common import json_encode, json_decode
import core.core
from core.exception import TaskException, SelfUpgradeException
from core.task_manager import TaskFactory
from core.interlocks import InterProcessLock, SingleInstanceError

class RunTaskWorkerCommand(object):
    """
    Helper class to run install/uninstall task
    """

    def __init__(self, core, task_id):
        self.core = core
        self.task_id = task_id

    def run(self):
        """
        Run task
        """
        # append web module to python path
        # check it's possible that we don't need this
        logging.debug("wait for task")
        line = sys.stdin.readline()
        task = core.core.parse_command(line)
        logging.info("start working on  task %i" % self.task_id)
        for item in task:

            command = core.core.gen_command({"command": "start_work_job", "job_id": item["job_id"]})
            # we print command to stdout cause master is capturing it
            print(command)
            result = None
            try:
                result = TaskFactory.execute_job(item)

            except TaskException as e:
                command = core.core.gen_command({"command": "error",
                                                 "job_id": item["job_id"],
                                                 "trace": e.traceback,
                                                 "message": e.message
                                                 })
                print(command)
                sys.exit(1)

            except SelfUpgradeException as e:
                parent_pid = e.parent_pid
                logging.info("helicon zoo is upgrading yourself %i" % parent_pid)
                sys.exit(13)

            except Exception as e:
                command = core.core.gen_command({"command": "error",
                                                 "job_id": item["job_id"],
                                                 "trace": traceback.format_exc(),
                                                 "message": str(e)
                                                 })
                print(command)
                sys.exit(1)



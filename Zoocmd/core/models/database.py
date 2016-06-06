import peewee
import datetime
import logging
import json
import core.core
import collections
from core.helpers.common import json_encode, json_decode, str_timestamp_to_datetime



STATUS_PENDING = 'pending'

class TaskPeewee(peewee.Model):
    created = peewee.DateTimeField(default=datetime.datetime.now)
    updated = peewee.DateTimeField(default=datetime.datetime.now)
    command = peewee.CharField(max_length=30)
    status = peewee.CharField(max_length=30, default=STATUS_PENDING)
    settings = peewee.TextField()
    def to_json(self):
        return json_decode({"task": self.id})

    class Meta:
        db_table = 'taskqueue_task'
        database = None

class JobPeewee(peewee.Model):

    """
    Задание на установку или удаление
    Сохраняет свое состояние в базе данных

    UI - создает его,
    воркер - читает и выполняет
    воркер обновляет статутс
    UI - показывает что задние выболнено, или ошибка

    для задания которое выполнялось, есть логи, они хранятся в LogMessage
    """

    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_DONE = 'done'
    STATUS_FAILED = 'failed'
    STATUS_CANCELED = 'canceled'

    STATUS_EXCEPTION = 'exception'
    LOCK = "running"

    COMMAND_INSTALL = 'install'
    COMMAND_UPGRADE = 'upgrade'
    COMMAND_UNINSTALL = 'uninstall'

    created = peewee.DateTimeField(default=datetime.datetime.now)
    updated = peewee.DateTimeField(default=datetime.datetime.now)
    title = peewee.CharField(max_length=100)
    command = peewee.CharField(max_length=30)
    params = peewee.TextField()
    status = peewee.CharField(max_length=30, default=STATUS_PENDING)
    settings = peewee.TextField()
    parent_pid = peewee.IntegerField(null=True)
    pid = peewee.IntegerField(null=True)
    task = peewee.ForeignKeyField(TaskPeewee, null=True)
    error_message = peewee.TextField(null=True)

    # dict description for session is needed by
    def dict_repr(self):
            representation = dict()
            representation["title"] = self.title
            representation["status"] = self.status
            representation['created'] = self.created.isoformat()
            representation['updated'] = self.updated.isoformat()
            representation['command'] = self.command
            representation['params'] = self.params
            representation['params_str'] = self.params
            representation['error_message'] = self.error_message
            if self.status in (JobPeewee.STATUS_DONE, JobPeewee.STATUS_FAILED):
                representation['is_finished'] = True
            else:
                representation['is_finished'] = False

            return representation



    class Meta:
        db_table = 'taskqueue_job'
        database = None

    def execute(self):
        """
        выполнить это задание, в этом процеесе
        выбрать параметре
        выбрать метод
        вывать у ядра нужный метод с параметрами
        ждать пока доделает

        это длинный и блокирующий метод, должен вызываться или из консоли, или из воркера
        никонгда из UI

        :raise ValueError:
        """
        if self.command == self.COMMAND_INSTALL:
            logging.debug("ok everything good i'm going to install")
            self.command_install()

        elif self.command == self.COMMAND_UPGRADE:
            self.command_upgrade()

        elif self.command == self.COMMAND_UNINSTALL:
            self.command_uninstall()

        else:
            raise ValueError('Invalid task command: {0}'.format(self.command))

    def command_install(self):
        state = json_decode(self.params)
        result = core.core.Core.get_instance().install(state['products'], state['parameters'],
                                                       False, True)
        state["parameters"] = result['parameters']
        self.params = json_encode(state)
        self.save()

    def command_upgrade(self):
        state = json_decode(self.params)
        result = core.core.Core.get_instance().upgrade(state['products'], state.get('parameters'))
        state["parameters"] = result['parameters']
        self.params = json_encode(state)
        self.save()

    def command_uninstall(self):
        state = json_decode(self.params)
        result = core.core.Core.get_instance().uninstall(state['products'], state.get('parameters'))
        state["parameters"] = result['parameters']
        self.params = json_encode(state)
        self.save()

    # DEPRECATED
    def add_log(self, record):
        """
        добавить лог запись в базу данных

        :param record:
        """
        PeeweeLogMessage.create(
            task=self,
            level=record.levelname,
            source='{0}.{1}'.format(record.module, record.funcName),
            message=record.msg
        )

    def get_logs(self, since=None):
        """
        :param since: str or int unix time to filter log messages
        :return: list of log message objects
        """
        if since is None:
            since = 0
        if isinstance(since, str):
            since = str_timestamp_to_datetime(since)

        log_messages = PeeweeLogMessage.select().where(PeeweeLogMessage.job == self,
                                                       PeeweeLogMessage.created >= since,
                                                       ).order_by(PeeweeLogMessage.id)
        # if since:
        #     if isinstance(since, str):
        #         since = str_timestamp_to_datetime(since)

        return [lm for lm in log_messages]

    def to_dict(self):
        """
        для сериализации в json

        :return:
        """
        return {
            'id': self.id,
            'created': self.created.isoformat(),
            'updated': self.updated.isoformat(),
            'title': self.title,
            'command': self.command,
            'params': json_decode(self.params) if self.params else None,
            'params_str': self.params,
            'status': self.status,
            'error_message': self.error_message,
            'is_finished': True if self.status in (self.STATUS_DONE, self.STATUS_FAILED, self.STATUS_CANCELED) else False
        }





class PeeweeLogMessage(peewee.Model):
    """
    Представляет собой 1 лог запись (обычно строка) в базе данных
    """
    task_id = peewee.IntegerField()
    job = peewee.ForeignKeyField(JobPeewee)
    created = peewee.DateTimeField(default=datetime.datetime.now)
    level = peewee.CharField(max_length=10)
    source = peewee.CharField(max_length=50)
    message = peewee.TextField()

    class Meta:
        db_table = 'taskqueue_logmessage'
        database = None

    def to_dict(self):
        return {
            'created': self.created.timestamp(),
            'level': self.level,
            'source': self.source,
            'message': self.message,
            'job_id': self.job.id
        }



# -*- coding: utf-8 -*-

import traceback
import threading
import logging
import time
import peewee
from .start import start
from .helpers.common import object_attrs_to_dict


class CoreLoader(object):
    """
    Реализует создание ядра в потоке, может говорить об этапе создания ядра (для прогресса на морде) и
    и об ошибках, которые случилист во время.

    """

    # статический экзампляр класса
    _instance = None

    # состояния загрузчика
    STATE_NONE = 'nihility'
    STATE_STARTING = 'starting'
    STATE_FAILED = 'failed'
    STATE_READY = 'ready'

    @classmethod
    def get_instance(cls):
        """
        Создаёт и возвращает загрузчик.
        :rtype : CoreLoader
        """
        if not cls._instance:
            cls._instance = CoreLoader()
        return cls._instance

    def __init__(self):
        """
        Конструктор.
        """
        self.state = self.STATE_NONE
        self.message = None
        self.errors = []
        self.error = None
        self.warnings = []
        self.warning = None
        self.thread = None
        # объект синхронизации для читать-писать состояние загрузчика
        self.state_lock = threading.Lock()

    def start(self, settings=None, make_sync=False):
        """
        Запустить поток, создающий ядро.
        :param settings: настройки, с которыми будет создавать ядро
        :param make_sync: делать ли синк ядра после создания
        """
        #self._start_thread(settings, make_sync)
        import core.core
        if settings is not None:
              core.core.DATABASE = peewee.SqliteDatabase(settings.database)

        if not self.thread or not self.thread.is_alive():
            # создать поток и запустить

            # for debugging purposes uncomment this line to run startup synchronously
            # self._start_thread(settings, make_sync)

            # for release next 3 lines should be used, comment them out for debug
            event_loop = core.core.core_event_loop
            callable_object = lambda: self._start_thread(settings, make_sync)
            event_loop.queue_work(callable_object)

    def clean_warnings(self):
        self.warnings = []
        self.warning = None

    def restart(self, settings=None):
        """
        Пересоздаёт ядро: удаляет текущее ядро и запускает поток для создания нового.
        :param settings:
        """
        # получить настройки
        from .core import Core
        settings = settings or Core.get_instance().settings
        logging.info('restarting core with settings: {}'.format(settings))
        # удалить текущее

        Core.drop_instance()
        # запустить создание нового
        self.start(settings, make_sync=True)

    def _start_thread(self, settings, make_sync=False):
        """
        Поток в котором создаётся ядро.
        :param settings: настройки для ядра
        :param make_sync: делать ли синк
        """
        try:
            with self.state_lock:
                self.state = self.STATE_STARTING

            self.set_state('Creating core...')

            # стартуем ядро
            core = start(settings)

            self.set_state('Loading feeds...')

            if make_sync:
                # делаем синк если нужно
                self.set_state('Loading feed...')
                core.get_feed()
                self.set_state('Searching installed products...')
                core.sync()

            with self.state_lock:
                # если были ошибки - сохраним их
                if core.error_manager.has_errors():
                    self.state = self.STATE_FAILED
                    self.errors = core.error_manager.format_errors()
                    self.error = core.error_manager.get_first()
                else:
                    self.state = self.STATE_READY

                if core.error_manager.has_warns():
                    self.state = self.STATE_READY
                    self.warnings = core.error_manager.format_warns()
                    self.warning = core.error_manager.get_first_warn()
                else:
                    self.state = self.STATE_READY

        except Exception as e:
            with self.state_lock:
                self.state = self.STATE_FAILED
                self.errors.append({
                    'message': '{0}'.format(e),
                    'traceback': traceback.format_exc()
                })
                self.error = e
                logging.error(traceback.format_exc())

    def set_state(self, message):
        """
        Устанавливает состояние загрузчика с синхронизацией
        :param message:
        """
        with self.state_lock:
            self.message = message
        logging.debug('Core loader: ' + message)

    def get_state(self):
        """
        Возвращает состояние загрузчика, синхронизировано.
        """
        with self.state_lock:
            return object_attrs_to_dict(self, ['state', 'errors', 'message', 'warnings'])

    def wait_core(self):
        """
        Ожидает завершения создания ядра (т.е. потока, в котором оно создаётся)
        и возвращает его.
        Используется для zoocmd, без веб-морды.
        :rtype : Core
        """
        from .core import Core

        logging.debug('Waiting for core')
        while True:
            with self.state_lock:
                if self.state == self.STATE_READY:
                    return Core.get_instance()
                if self.state == self.STATE_FAILED:
                    raise RuntimeError('Core creation failed') from self.error
            time.sleep(1)


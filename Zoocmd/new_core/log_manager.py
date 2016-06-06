# -*- coding: utf-8 -*-

import os
import os.path
import datetime


class LogManager(object):
    """
    Хелпер, который может получать и создавать директории для логов продукта.
    Эти логи случаются во время инсталляции, апгрейда, деинсталляции.
    Получает полный путь с учетом zoo_home, имени продукта, даты
    """

    # статический экземпляр
    _lm = None

    @classmethod
    def get_instance(cls, core):
        """
        Возвращает или создаёт экземпляр класса.
        :rtype : LogManager
        """
        if not cls._lm:
            cls._lm = LogManager(core)

        return cls._lm

    def __init__(self, core):
        self.core = core
        self.root = self.core.settings.logs_path

    def get_log_path(self, product, action):
        """
        Возвращает путь к логу для продукта product для процесса action ('install', 'uninstall',...)
        :param product: BaseProduct или имя продукта
        :param action: действие для которого нужно сделать лог файл: install, uninstall, ...

        Сгенерировать имя файла, и вернуть полный путь для лог файла
        примеры:
        C:\Zoo4\ZooInstaller\logs\Helicon.Zoo\2014-10-07-17-11-01-install_msi.log
        C:\Zoo4\ZooInstaller\logs\Strawberry.Perl\2014-09-30-17-53-36-uninstall_msi.log
        """

        dir_path = self.get_log_dir(product)
        dt = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        file_name = '{0}-{1}.log'.format(dt, action)

        return os.path.join(dir_path, file_name)

    def get_log_dir(self, product):
        """
        Возвращает директорию лого для продукта, создайт ее, если она не существует.
        :param product: BaseProduct или имя продукта
        """
        from .models.base_product import BaseProduct
        if isinstance(product, BaseProduct):
            name = product.name
        else:
            name = str(product)
        dir_path = os.path.join(self.root, name)
        os.makedirs(dir_path, exist_ok=True)

        return dir_path



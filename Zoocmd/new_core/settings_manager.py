"""
Copyright © Helicon Tech. All rights reserved.

Модуль, заведующий всеми общесистемными настройками. Все пути, константы и пр. должны быть заданы тут.
"""

import os
import os.path
import platform
import yaml
import logging

from new_core.version import VERSION


# главный фид, он не появляется в настрофках в морде, он тут захардкожен
MAIN_FEED = 'http://ci-helicontech/zoo4/feed.yaml'
try:
    # возможность переопределить главный фид
    # фича для разработчика в модуле local_feed
    import local_feed
    MAIN_FEED = local_feed.MAIN_FEED
except:
    pass


# путь по умолчанию к файлу с настройками
DEFUALT_SETTINGS_FILE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..\..\etc\settings.yaml'))


class Settings(object):
    """
    Класс который умеет загружать, хранить и отдавать настройки ядра.
    Не синглтон! Может быть много разных вариантов настроек.
    В будущем они будут передаваться высокоуровневым функциям ядра, как опции.
    """

    def __init__(self, **kwargs):
        """
        Конструктор настроек.
        Тут задаются значения по умолчанию для всех важных констант в программе
        :param kwargs: словарь с настройками, обычно загруженный из файла или взятый из старого ядра при пересоздания
        ядра.
        """

        if 'path' in kwargs:
            del kwargs['path']

        uname = platform.uname()

        # Выставляем дефолтные значения
        # Вначале для изменяемых параметров

        # сохраним путь к файлу с настройками
        self.path =  DEFUALT_SETTINGS_FILE
        # корень проекта
        self.root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..\..'))
        # диретория кеша
        self.cache_path = os.path.join(self.root, 'cache')
        self.logs_path = os.path.join(self.root, 'logs')
        self.tmp_logs_path = os.path.join(self.root, 'tmp')
        self.supervisor_logpath = os.path.join(self.root, 'supervisor.log')
        # диктория для хранения ямлов, БД, installed, current, ...
        self.storage_path = os.path.join(self.root, 'data')
        self.database = os.path.join(self.storage_path, 'db.sqlite3')
        # урлы фидов
        self.feed_urls = [] # Additional custom feeds
        # битность, может задавать в настройках, но обычно нет
        self.bitness = '64' if uname.machine.find('64') > 0 else '32'
        # веб сервер, по умолчанию IIS
        self.webserver = 'iis'
        # язык
        self.lang = 'english'
        # директория, куда ставятся все продукты
        self.zoo_home = os.path.normpath(os.path.join(self.root, '..'))

        # Теперь сольем с параменрами
        self.__dict__.update(kwargs)

        # Теперь сбросим неизменяемые параметры
        self.main_feed_url = MAIN_FEED  # Главный фид лучше иметь отдельно
        # ос не задается в настройках
        self.os = uname.system.lower()
        # версия ос не задается в настройках
        self.os_version =  uname.version
        # версия Zoo
        self.version = VERSION

        # Файлы для хранения фидов
        self.main_feed_path = os.path.join(self.storage_path, 'main.yaml'.format(self.webserver))
        self.current_feed_path = os.path.join(self.storage_path, 'current.yaml')
        self.installed_feed_path = os.path.join(self.storage_path, 'installed.yaml')
        self.engines_feed_path = os.path.join(self.storage_path, 'engines-{0}.yaml'.format(self.webserver))



    def __repr__(self):
        return '{0}'.format(self.to_dict())

    def get_platform(self):
        """
        Создаёт и возвращает объект Платформы.
        """
        from .models.platform import Platform
        return Platform(os=self.os,
                        bitness=self.bitness,
                        os_version=self.os_version,
                        lang=self.lang,
                        web_server=self.webserver)

    # def get_state(self):
    #     """
    #     Сериализует настройки для дальнейшего сохранения в файл или передачи в json.
    #     """
    #     return {
    #         'version': self.version,
    #         'root': self.root,
    #         'cache_path': self.cache_path,
    #         'logs_path': self.logs_path,
    #         'storage_path': self.storage_path,
    #         'urls': self.urls,
    #         'os': self.os,
    #         'os_version': self.os_version,
    #         'bitness': self.bitness,
    #         'webserver': self.webserver,
    #         'lang': self.lang,
    #         'zoo_home': self.zoo_home
    #     }

    def to_dict(self):
         """
         TODO: Удалить ненужную функцию
         """
         return self.__dict__

    def update(self, data):
        """
        Обновляет настройкию
        :param data: словарь с настройкаи, которые нужно обновить.
        """

        # fix empty url
        if 'feed_urls' in data:
            data['feed_urls'] = [url for url in data['feed_urls'] if url]

        # fix empty strings to null
        for key, val in data.items():
            if val == '':
                data[key] = None
        self.__init__(**data)

    def format(self):
        """
        Форматирует настройки для вывода строкой как yaml.
        """
        return yaml.dump(self.to_dict())


"""
Глобальные функции:
"""


def load_settings(stream=None):
    """
    Загружает файл настроек и возвращает объект настроек Settings.
    :rtype : Settings
    """
    if not stream:
        # По умолчанию грузим из файла
        path = DEFUALT_SETTINGS_FILE
        if os.path.exists(path):
            logging.debug('loading settings file: {0}'.format(path))
            # загружаем ямл и десериализуем его
            with open(path, 'r') as f:
                data = yaml.load(f)
                data['path'] = path
    else:
        data = yaml.load(stream)
    return Settings(**data)




def save_settings(settings, stream=None):
    """
    Сохраняет настройки в файл в ямл
    Сохраняются только те настройки, которые отличаются от дефолтных.
    :param settings:
    :param file_path:
    :return:
    """

    # Образец с дефолтными значениями для сравнения
    templ = Settings()


    # Вырезаем только записи, отличающиеся от дефолтных
    data = dict((key,val) for key,val in settings.__dict__.items() if (key not in templ.__dict__) or val!=templ.__dict__[key])

    #Записи, которые не должны попасть в файл в любом случае
    data.pop('path', None)
    data.pop('main_feed_url', None)

    # Сохраняем ямл
    if not stream:
        logging.debug('saving settings file: {0}'.format(settings.path))
        with open(settings.path, 'w') as f:
            yaml.dump(data,f)
    else:
        yaml.dump(stream)


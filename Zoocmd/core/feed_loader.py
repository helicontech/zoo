# -*- coding: utf-8 -*-

import sys
import os.path
import logging
import yaml
from urllib import request
from urllib.parse import urlparse, urljoin
from collections import Iterable, Sized
import codecs
from core.exception import FeedLoaderDownload

from core.core import Core
from core.helpers.common import is_local_file
from core.helpers import yaml_loader
from core.version import VERSION


class FeedLoaderError(Exception):
    pass



class FeedLoader(object):
    """
    загрузчик фида,
    умеет загружать фид
        - из директории с под-директориями
        - из yaml файла
        - из yaml url
    """
    def __init__(self, core, *urls):
        self.core = core
        self.urls = urls

    def load(self):
        result = []

        for url in self.urls:
            if is_local_file(url) and not os.path.isabs(url):
                logging.debug('build norm_url from "{0}" and "{1}"'.format(self.core.settings.zoo_home, url))
                norm_url = os.path.join(self.core.settings.zoo_home, url)
                norm_url = os.path.normpath(norm_url)
            else:
                norm_url = url

            items = None
            try:
                fli = FeedLoaderFactory.create_feed_loader_item(norm_url)
                items = fli.load_yaml()
            except FeedLoaderDownload as ex:
                self.core.error_manager.add_non_critical(ex)
            except Exception as ex:
                self.core.error_manager.add(ex)

            if items:
                if not isinstance(items, (Iterable, Sized)):
                    raise FeedLoaderError("Data loaded from {0} is not list".format(url))

                logging.debug('loaded: {0} items'.format(len(items)))
                result.extend(items)

        return result


class FeedLoaderBase(object):
    """
    Базовый класс для загрузчика
    его надо переопредялть всем реализациям
    """
    def __init__(self, url):
        self.url = url
        self.modified_time = 0

    def load_yaml(self):
        return []

    def _patch(self, path):
        return path

    def patch_file_path(self, data):
        """
        Подвправить путь для статтического файла, если нужно
        для иконок, для файлов которые в локальной диретории нужно пересчитать относительный путь в абсолютный
        :param data:
        :return:
        """
        if data is None:
            return

        for product in data:
            if "icon" in product:
                product["icon"] = "{0}".format(self._patch(product["icon"], product))

            if "files" in product:
                if product["files"] is None:
                    continue
                for file in product["files"]:
                    file["file"] = self._patch(file["file"], product)


class FeedLoaderUrl(FeedLoaderBase):
    """
    загрузчик фида из url
    загружает 1 большой yaml по http, указывая Zoo Agent в качестве агента
    исправляет ссылки на файлы, так чтобы они указывали на тот домен откуда был скачан сам url
    """
    def __init__(self, url):
        super().__init__(url)
        if is_local_file(url):
            raise Exception("Url '{0}' is not external url".format(url))

    def load_yaml(self):
        logging.debug("Loading from '{0}'".format(self.url))

        try:
            headers = {
                'User-Agent': 'Zoo Agent {0}; {1}'.format(VERSION, Core.get_instance().settings.get_platform().__repr__())
            }
            req = request.Request(self.url, headers=headers)
            stream = request.urlopen(req)
            # stream = request.urlopen(self.url, headers = headers)
        except Exception as ex:
            raise RuntimeError('Could not load url {0}'.format(self.url)) from ex
        # TODO move to yaml_helper
        items = yaml.load(
            stream,  # TODO: read Last-Modified header
            yaml_loader.YamlLoader)

        self.patch_file_path(items)

        if items is None:
            items = []
        return items

    def _patch(self, path, product):

        path = path.replace(".\\", "").replace("\\", "/")

        file_full_path = urljoin(self.url, path)
        return file_full_path


class FeedLoaderFile(FeedLoaderBase):
    """
    загружает yaml из локального файла
    исправляет относительные пути на относительные, с учетом того пути где лежит этот yaml файл
    """
    def __init__(self, url):
        super().__init__(url)
        if not os.path.isfile(url):
            raise Exception("Url '{0}' is not file".format(url))

    def load_yaml(self):
        logging.debug("Loading from '{0}'".format(self.url))
        self.modified_time = os.path.getmtime(self.url)

        try:
            #stream = open(self.url, 'r')
            stream = codecs.open(self.url, 'r', 'utf-8')
        except Exception as ex:
            raise RuntimeError('Could not load url {0}'.format(self.url)) from ex


        items = yaml.load(
            stream,
            yaml_loader.YamlLoader)

        self.patch_file_path(items)
        if items is None:
            items = []
        return items

    def _patch(self, path, product):
        """
        не исправлять url и абсалютные пути
        :param path:
        :return:
        """
        if not is_local_file(path):
            return path

        if os.path.isabs(path):
            return path


        full_path = self.url
        local_file_full_path = os.path.join(os.path.dirname(full_path), path)
        return local_file_full_path


class FeedLoaderDir(FeedLoaderBase):
    """
    Загрузчик директории
    рекурсивно заходит вглубь указанной  директории, находит yaml файлы
    и поштучно их загружает с помошью FeedLoaderFile
    полученые продукты добавляет себе в список
    """
    def __init__(self, url):
        super().__init__(url)
        if not os.path.isdir(url):
            raise Exception("Url '{0}' is not directory".format(url))

        self.flf = []

    def load_yaml(self):
        logging.debug("Loading from '{0}'".format(self.url))
        self.flf = []
        for root, dirs, files in os.walk(self.url):
            for f in files:
                if not f.lower().endswith(".yaml"):
                    continue
                full_path = os.path.join(root, f)
                self.flf.append(FeedLoaderFile(full_path))

        result = []
        for l in self.flf:
            result.extend(l.load_yaml())
        return result


class FeedLoaderFactory(object):
    """
    Фабрика умеет создавать FeedLoader -ы на основании url
    """
    @staticmethod
    def create_feed_loader_item(url):
        if not is_local_file(url):
            return FeedLoaderUrl(url)

        if os.path.isdir(url):
            return FeedLoaderDir(url)

        if os.path.isfile(url):
            return FeedLoaderFile(url)

        raise FeedLoaderDownload("Could not load url '{0}'".format(url))


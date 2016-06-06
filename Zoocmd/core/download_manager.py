# encoding: utf-8

import os
import threading
import logging
import hashlib
import shutil

import requests

from core.downloader_cache import DownloaderCache
from core.helpers.common import is_local_file


class DownloadError(Exception):
    pass


class DownloadThread(threading.Thread):

    def __init__(self, **kwargs):
        super(DownloadThread, self).__init__(**kwargs)
        self.failed = False


class DownloadManager(object):
    """
    Реализует загрузчик файлов в несколько потоков.
    """

    def __init__(self, core, product):
        self.core = core
        self.threads = []
        self.product = product
        # объякт кеша, который знает куда загружать файлы и под каким именем
        self.cache = DownloaderCache(product)
        # создать директории для кеша
        self.cache.assert_dirs()

    def download(self, files):
        """
        Загружает файлы из списка в несколько потоков.
        :param files: список урлов для загрузки
        """
        logging.info('Begin download {0} files'.format(len(files)))
        for f in files:
            self.download_single(f)

        # ждём окончания загрузок
        self.wait()
        # проверяем хеши
        self.check_checksum(files)

    def download_single(self, file):
        """
        Загржает одиночный файл. Если это локальный файл - просто копирует в кеш,
        если урл - загружает в отдельном потоке.
        :param file:
        """
        url = file.file
        headers = file.headers
        cookies = file.cookies
        if is_local_file(url):
            # это локальный файл
            local_file = url
            shutil.copy(local_file, file.path)
            logging.info('local file: {0}'.format(url))
        else:
            # урл
            if not self.cache.is_in_cache(file.filename):
                # в кеше нет
                logging.info('begin download: {0}'.format(url))
                # создаём поток для загрузки
                t = DownloadThread(
                    target=self.process_download,
                    name='Downloading of ' + url,
                    args=(url, file, headers, cookies)
                )
                self.threads.append(t)
                t.daemon = True
                # стратуем его
                t.start()
            else:
                # уже есть в кеше
                logging.info('{0} found in cache'.format(file))

    def process_download(self, source_url, file, headers=None, cookies=None):
        """
        Поток загружающий файл.
        :param source_url: что загружать
        :param file: объект File, знает куда сохранять, это путь в кеше
        :param headers: опциональные залоговки для хттп-запроса
        :param cookies: опциональные куки для хттп-запроса
        """
        try:
            file_name = self.cache.get_filename_from_url(source_url)
            logging.info('starting download of {0} to {1}'.format(source_url, file))

            downloaded_length = 0
            with open(file.path, "wb") as f:
                # создаем запрос
                s = requests.Session()
                if headers is not None:
                    s.headers = headers
                if cookies is not None:
                    for cookie in cookies:
                        s.cookies = requests.utils.cookiejar_from_dict(cookie, s.cookies)
                # делаем запрос
                response = s.get(source_url, stream=True, verify=False)
                if response.status_code != 200:
                    raise DownloadError('{0}: Response status code is {1}'.format(source_url, response.status_code))

                content_length = response.headers.get('content-length')
                if content_length is None:
                    # no content length header
                    downloaded_length = len(response.content)
                    f.write(response.content)
                else:
                    # длина ответа известна, читаем из потока кусочками
                    content_length = int(content_length)
                    length_step = self._get_length_step(content_length)
                    for data in response.iter_content(length_step):
                        downloaded_length += len(data)
                        # и записываем в файл в кеше
                        f.write(data)
                        logging.info('{0}: {1:.0f} Kb of {2:.0f} Kb ({3:.1f}%)'.format(
                            file_name,
                            downloaded_length / 1024.0,
                            content_length / 1024.0,
                            downloaded_length / content_length * 100.0))

            if not downloaded_length:
                raise DownloadError('size of downloaded file {0} is too small: {1} bytes'.format(
                    file_name, downloaded_length))
        except Exception:
            threading.current_thread().failed = True
            if os.path.exists(file.path):
                os.remove(file.path)
            raise

        logging.debug('download of {0} complete. {1} bytes'.format(file_name, downloaded_length))

    def wait(self):
        """
        Ожидает завершения всех загружающих потоков.
        """
        for t in self.threads:
            t.join()
            if t.failed:
                raise RuntimeError('Failed: {0}'.format(t.name))

        logging.info('all downloads completed')
        del self.threads[:]

    @staticmethod
    def _get_length_step(content_length):
        """
        Рассчитывает длину чанка, которым мы будет загружать и логгировать.
        """
        if content_length > 100 * 1024 * 1024:
            length_step = int(content_length / 20)
        else:
            length_step = int(content_length / 10)

        length_step = max(length_step, 1024 * 1024)
        return length_step


    @staticmethod
    def check_checksum(files):
        """
        Проверяет хэши загруженных файлов, если они были указаны в ямле.
        :param files: списков фалов для проверки
        """
        # цикл по файлам
        for f in files:
            logging.debug(f.path)
            hash_method = None
            hash_origin = None
            # есть ли какой-то хэш для файла?
            if f.sha1:
                hash_method = hashlib.sha1
                hash_origin = f.sha1
            elif f.md5:
                hash_method = hashlib.md5
                hash_origin = f.md5

            if f.path and hash_method:
                # считаем хеш
                hash_calculated = DownloadManager.get_hash_value(hash_method, f.path)
                # и сравниваем
                if hash_origin.lower() != hash_calculated.lower():
                    # хэши не совпали
                    if os.path.exists(f.path):
                        # удалим файл из кеша
                        os.remove(f.path)
                    # из выбросим ошибку
                    raise DownloadError('Checksum for {0} is {1}, but {2} expected'.format(
                        f.path, hash_calculated, hash_origin))

    @staticmethod
    def get_hash_value(hash_method, path):
        """
        Возвращает хеш файла.
        :param hash_method: функция, которая считает хеш
        :param path: путь к файлу
        :return:
        """
        with open(path, 'rb') as f:
            return hash_method(f.read()).hexdigest()
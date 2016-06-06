# -*- coding: utf-8 -*-

from core.downloader_cache import DownloaderCache


class File(object):
    """
    Represents file object for product.
    """

    def __init__(self, product, **kwargs):
        """
        Create File object.
        :param product: parent product,
        :param kwargs: dict from product yaml representation, example:
                file:
                - file: http://...
                  filename: qwe.msi (optional)
                  sha1: 384750934857 (optional)
                  md5: 9586749 (optional)
                  headers: (optional)
                  - h1: v1
                  cookies: (optional)
                  - c1: b1
        """
        self.product = product

        # file url
        self.file = kwargs['file']
        # DownloaderCache knows how to get filename (without direcotry) from urls
        cache = DownloaderCache(product)
        # use 'filename' from args or get from cache
        self.filename = kwargs.get('filename', cache.get_filename_from_url(self.file))
        # physical path to file in cache
        self.path = cache.get_path(self.filename)

        # optinal args
        # sha1 hash to check file file checksum after downloading
        self.sha1 = kwargs.get('sha1')
        # md5 hash
        self.md5 = kwargs.get('md5')
        # headers to use in http client to download file
        self.headers = kwargs.get('headers')
        # cookies to use in http client to download file (used in JDK)
        self.cookies = kwargs.get('cookies')

    def __repr__(self):
        return 'File({0})'.format(self.filename)

    def __getstate__(self):
        """
        Represents File object to dict. Used in yaml and json representaion.
        :return:
        """
        result = dict()
        if self.file:
            result['file'] = self.file
        if self.filename:
            result['filename'] = self.filename
        if self.sha1:
            result['sha1'] = self.sha1
        if self.md5:
            result['md5'] = self.md5
        if self.headers:
            result['headers'] = self.headers
        if self.cookies:
            result['cookies'] = str(self.cookies)

        return result


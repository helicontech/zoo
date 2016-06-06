# -*- coding: utf-8 -*-

import platform

from ..version_comparer import OsComparer
from ..helpers.version import compare_versions


class PlatformError(Exception):
    pass


class Platform(object):
    """
    Represents platform as collection os (name), os_version, bitness, web_server, lang attributes.
    Main goal of this class is match platforms to filter products for current core platform.
    """

    OS_WINDOWS = 'windows'
    OS_DEBIAN = 'debian'
    OS_UBUNTU = 'ubuntu'
    OS_CENT = 'centos'
    OSes = (OS_WINDOWS, OS_DEBIAN, OS_UBUNTU, OS_CENT)

    BITNESS_32 = '32'
    BITNESS_64 = '64'

    WEB_SERVER_IIS = 'iis'
    WEB_SERVER_IIS_EXPRESS = 'iisexpress'
    WEB_SERVER_APACHE = 'apache'
    WEB_SERVER_NGINX = 'nginx'
    WEB_SERVERS = (WEB_SERVER_IIS, WEB_SERVER_IIS_EXPRESS, WEB_SERVER_APACHE, WEB_SERVER_APACHE, WEB_SERVER_NGINX)

    def __init__(self, os=None, bitness=None, web_server=None, lang=None, os_version=None):
        if os:
            # set os
            self.os = os.lower()
            if os_version:
                # set os version
                self.os_version = os_version
                self.os_comparer = None
            else:
                # if no os version, athe create os comparer
                self.os_version = None
                self.os_comparer = OsComparer(self.os)
                self.os = self.os_comparer.name
        else:
            # no info about os
            self.os = None
            self.os_version = None
            self.os_comparer = None

        if bitness:
            # set bitness
            self.bitness = str(bitness).lower()
            if self.bitness not in (self.BITNESS_32, self.BITNESS_64):
                raise PlatformError('unknown bitness: {0}'.format(self.bitness))
        else:
            self.bitness = None

        if web_server:
            # set web server
            self.web_server = web_server.lower()
            if self.web_server not in self.WEB_SERVERS:
                raise PlatformError('unknown web server: {0}'.format(self.web_server))
        else:
            self.web_server = None

        # set lang
        self.lang = lang.lower() if lang else None

    def __repr__(self):
        """
        Returns string representaion of platform.
        """
        return 'Platform({0}.{1}.{2}.{3}.{4})'.format(
            self.os or '*',
            self.os_version or '*',
            self.bitness or '*',
            self.web_server or '*',
            self.lang or '*'
        )

    @classmethod
    def get_current_os(cls):
        """
        Returns runtime OS python platform api.
        """
        s = platform.system()
        if s.startswith('Win'):
            return cls.OS_WINDOWS

        raise PlatformError('unknown platform: ' + s)

    @classmethod
    def get_current_bitness(cls):
        """
        Returns runtime bitness.
        """
        m = platform.machine()
        if m.index('64') >= 0:
            return cls.BITNESS_64

        return cls.BITNESS_32

    def match(self, other):
        """
        Matches platform with other.
        Used for filtering product by current core platform.
        :type other: Platform
        """
        if self.os:
            if self.os_version:
                if other.os_version:
                    if self.os != other.os:
                        return False
                    if compare_versions(self.os_version, other.os_version) != 0:
                        return False
                elif other.os_comparer:
                    if not other.os_comparer.match(self.os, self.os_version):
                        return False
            elif self.os_comparer:
                if other.os_version:
                    if not self.os_comparer.match(other.os, other.os_version):
                        return False
                elif other.os_comparer:
                    if self.os != other.os:
                        return False
        if self.bitness and other.bitness:
            if self.bitness != other.bitness:
                return False
        if self.web_server and other.web_server:
            if self.web_server != other.web_server:
                return False
        if self.lang and other.lang:
            if self.lang != other.lang:
                return False
        return True

    @classmethod
    def from_product_dict(cls, **data):
        """
        Creates Platform instance from product yaml representaion.
        :param data:
        :return:
        """
        return Platform(
            os=data.get('os'),
            bitness=data.get('bitness'),
            web_server=data.get('webserver'),
            lang=data.get('lang')
        )


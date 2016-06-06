# -*- coding: utf-8 -*-

from core.helpers.urls import add_trailing_slash


class Site(object):
    """
    Represents IIS site. Used in IIS(BaseWebServer) class.
    """
    def __init__(self, name, bindings=None, default_app=None, applications=None):
        self.default_app = default_app
        self.bindings = bindings
        self.name = name
        self.applications = applications or []
        # build url for every binding, used in server tree.
        self.urls = []
        for binding in self.bindings:
            if binding[0] in ('http', 'https'):
                self.urls.append(self.url_from_binding(binding[0], binding[1]))
                self.port = int(Site.port_from_binding(binding[1]))

    def __str__(self):
        return "{0}".format(self.name)

    def to_dict(self):
        """
        Dumps to dict for ajaj-communication.
        """
        return dict(
            name=self.name,
            bindings=self.bindings,
            defaultApp=self.default_app,
            applications=[app.path for app in self.applications],
            urls=self.urls,
            port=self.port
        )


    @staticmethod
    def port_from_binding(info):
        parts = info.split(':')
        if len(parts) != 3:
            return 'Broken binding info: ' + info
        port = parts[1]
        return port

    @staticmethod
    def url_from_binding(protocol, info):
        """
        Builds url for binding.
        """
        parts = info.split(':')
        if len(parts) != 3:
            return 'Broken binding info: ' + info
        addr = parts[0]
        port = parts[1]
        hostname = parts[2]

        return '{0}://{1}{2}/'.format(
            protocol,
            hostname if hostname else addr if addr != '*' else 'localhost',
            ':{0}'.format(port) if port != '80' else ''
        )


class SiteApplication(object):
    """
    Represents IIS app. Used in IIS(BaseWebServer) class.
    """
    def __init__(self, path, pool):
        #logging.debug("SiteApplication({0},{1})".format(path, pool))
        self.path = path
        self.pool = pool

    def __str__(self):
        return "{0}".format(self.path)


class SiteVirtialDirectory(object):
    """
    Represents IIS virtual directory. Used in IIS(BaseWebServer) class.
    """
    def __init__(self, path, physical_path):
        #logging.debug("SiteVirtialDirectory({0},{1})".format(path, physical_path))
        self.path = add_trailing_slash(path)
        self.physical_path = physical_path

    def __str__(self):
        return "{0}".format(self.path)

    def __repr__(self):
        return self.__str__()


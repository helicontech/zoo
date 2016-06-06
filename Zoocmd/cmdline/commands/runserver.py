# -*- coding: utf-8 -*-

import os
import os.path
import sys
import logging
import subprocess
import web.urls
import tornado.ioloop
import tornado.web
import web.web_settings
import web.taskqueue.tornado_worker
import web.zooapi.views.tornado_console
import logging
import core.core

class RunServerCommand(object):
    """
    Helper class to start web ui django server
    """

    def __init__(self, settings, port):
        self.settings = settings
        self.port = port

    def run(self):
        """
        run tornado server
        """
        # add web module to python path
        sys.path.append(os.path.join(self.settings.root, 'src', 'web'))
        urls = web.urls.application_urls
        worker = web.taskqueue.tornado_worker.TornadoWorker.create_instance()
        console = web.zooapi.views.tornado_console.TornadoConsole.create_instance()
        # adding web static handler to the urls list
        static_handler = (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": web.web_settings.STATIC_PATH})
        favicon_handler = (r"/(favicon\.ico)", tornado.web.StaticFileHandler, {"path": web.web_settings.STATIC_PATH})
        web_applio = TornadoServer(int(self.port),
                                   urls + [static_handler,favicon_handler] + worker.application_handlers + console.application_handlers
                                   )
        # start event loop
        core.core.core_event_loop_start()


class TornadoServer(object):

    def __init__(self, *args):
        self.port = args[0]
        self.application = tornado.web.Application(args[1])
        self.main_loop = tornado.ioloop.IOLoop.instance()
        self.application.listen(self.port)





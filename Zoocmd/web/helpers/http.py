# -*- coding: utf-8 -*-
"""
    Collection of classes that we will use to override django
"""
import tornado.web
import traceback
import sys
import core.core_loader
import core.core
import web.zoo.views
import web.zooapi.views

# http request class synonym of django request
class HttpRequest:
        def __init__(self, *args, **kwargs):
            self.tornado_http_request = kwargs.get("request")
            self.handler = kwargs.get("backend")
            request = self.tornado_http_request
            self.name = kwargs.get("name")
            self.method = request.method
            self.body = request.body
            self.GET = {}
            self.POST = {}
            self.REQUEST = {}
            self.COOKIES = self.handler.cookies

            for key in request.query_arguments.keys():
                self.GET[key] = request.query_arguments[key]
                temp = self.GET[key]
                new_tmp = []
                for item in temp:
                    new_tmp.append(item.decode())
                self.GET[key] = new_tmp

                if len(self.GET[key]) == 1:
                    self.GET[key] = self.GET[key][0]

            for key in request.body_arguments.keys():
                self.POST[key] = request.body_arguments[key]
                temp = self.POST[key]
                new_tmp = []
                for item in temp:
                    new_tmp.append(item.decode())
                self.POST[key] = new_tmp

                if len(self.POST[key]) == 1:
                    self.POST[key] = self.POST[key][0]

            for key in request.arguments.keys():
                self.REQUEST[key] = request.arguments[key]

                temp = self.REQUEST[key]
                new_tmp = []
                for item in temp:
                    new_tmp.append(item.decode())
                self.REQUEST[key] = new_tmp

                if len(self.REQUEST[key]) == 1:
                    self.REQUEST[key] = self.REQUEST[key][0]


# http response class synonym of django response
class HttpResponse:
    def __init__(self, **kwargs):
        status_code = kwargs.get("status_code", 200)
        body = kwargs.get("body", "")
        headers = kwargs.get("headers", [])
        super(HttpResponse, self).__setattr__('status_code', status_code)
        super(HttpResponse, self).__setattr__('body', body)
        d = {}
        for (k, v) in headers:
            d[k] = v
        super(HttpResponse, self).__setattr__('headers', d)

    def get_headers(self):
        for i in self.headers:
            yield (i, self.headers[i])

    def add_header(self, name: str, value: str) -> bool:
        self.headers[name] = value
        return True

    # for easy setting custom headers
    def __setattr__(self, k, v):
        if k in ("status_code", "body", "headers"):
            self.__dict__[k] = v
        else:
            self.__dict__["headers"][k] = v

    def __setitem__(self, k, v):
        if k in ("status_code", "body", "headers"):
            self.__dict__[k] = v
        else:
            self.__dict__["headers"][k] = v


    def set_headers(self, hdrs: list) -> bool:
        self.headers = {}
        for (k, v) in hdrs:
            self.headers[k] = v
        return True


# http not allowed class of django response not allowed
class HttpResponseNotAllowed(HttpResponse):
    def __init__(self, not_allowed, **kwargs):
        super().__init__(**kwargs)
        status_code = 405
        not_allowed = not_allowed
        body = "Method not ALLOWED"
        super(HttpResponse, self).__setattr__('status_code', status_code)
        super(HttpResponse, self).__setattr__('body', body)
        super(HttpResponse, self).__setattr__('not_allowed', not_allowed)


class HttpResponseRedirect(HttpResponse):
    def __init__(self, redirect_to, **kwargs):
        super().__init__(**kwargs)
        status_code = 301
        body = "REDIRECT TO "
        super(HttpResponse, self).__setattr__('status_code', status_code)
        super(HttpResponse, self).__setattr__('body', body)
        super(HttpResponse, self).__setattr__('redirect_to', redirect_to)


class HttpResponseServerError(HttpResponse):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        status_code = 500
        body = "Error page"
        super(HttpResponse, self).__setattr__('status_code', status_code)
        super(HttpResponse, self).__setattr__('body', body)


# common handler for processing http request through tornado
class SettingsRequestHandler(tornado.web.RequestHandler):

    def initialize(self, callable_object, name, appname):
        self.callable = callable_object
        self.url_name = name

    def get(self):
        # may context doesn't need all params that we have, and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self))
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

    def post(self):
        # may context doesn't need all params that we have,
        # and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self))
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

    def render_low_level_mistake(self, mistake_body):
        self.clear()
        self.set_status(500)
        self.write(mistake_body)
        self.finish()
    # render response to the client
    def render_http_response(self, response):
            self.clear()

            if response.status_code == 301 or response.status_code == 302:
                self.redirect(response.redirect_to, status=response.status_code)
                return

            self.set_status(response.status_code)

            for header in response.get_headers():
                (name, value) = header
                self.add_header(name, value)

            self.write(response.body)
            self.finish()


# common handler for processing http request through tornado
class CommonRequestHandler(tornado.web.RequestHandler):
    def render_low_level_mistake(self, mistake_body):
        self.clear()
        self.set_status(500)
        self.write("<html><body><pre>" + mistake_body + "</pre></body></html>")
        self.finish()



    def initialize(self, callable_object, name, appname):
        needed_state = core.core_loader.CoreLoader.STATE_READY
        core_loader = core.core_loader.CoreLoader.get_instance()

        core_loaders_state = core_loader.get_state()
        if core_loaders_state["state"] != needed_state:
            if appname == "api":
                self.callable = lambda *args: web.zooapi.views.core.state(args[0])
            else:
                self.callable = lambda *args: web.zoo.views.wait_core(args[0])
        else:
            Сore = core.core.Core.get_instance()
            if Сore.settings.webserver is None and appname != "api":
                self.callable = lambda *args: web.zoo.views.select_webserver(args[0])
            else:
                self.callable = callable_object

        self.url_name = name

    def get(self):
        # may context doesn't need all params that we have, and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self))
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

    def post(self):
        # may context doesn't need all params that we have,
        # and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self))
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

    # render response to the client
    def render_http_response(self, response):
            self.clear()

            if response.status_code == 301 or response.status_code == 302:
                self.redirect(response.redirect_to, status=response.status_code)
                return

            self.set_status(response.status_code)

            for header in response.get_headers():
                (name, value) = header
                self.add_header(name, value)

            self.write(response.body)
            self.finish()

# common handler for processing http request through tornado with one param in url
class CommonRequestHandlerTwoParam(CommonRequestHandler):

    def initialize(self, *args, **kwargs):
       super().initialize(*args, **kwargs)

    def post(self, param1, param2):
        # may context doesn't need all params that we have, and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self), param1, param2)
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

    def get(self, param1, param2):
        # may context doesn't need all params that we have, and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self), param1, param2)
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

# common handler for processing http request through tornado with one param in url
class CommonRequestHandlerOneParam(CommonRequestHandler):

    def initialize(self, *args, **kwargs):
       super().initialize(*args, **kwargs)


    def post(self, param1):
        # may context doesn't need all params that we have,
        #  and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self), param1)
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)

    def get(self, param1):
        # may context doesn't need all params that we have,
        #  and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self), param1)
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)


# common handler for processing http request through tornado for icon path
class IconRequestHandler(CommonRequestHandler):

    def initialize(self, *args, **kwargs):
       super().initialize(*args, **kwargs)

    def get(self, product_name):
        # may context doesn't need all params that we have, and there is some sense to change it to specific object
        try:
            response = self.callable(HttpRequest(request=self.request, name=self.url_name, backend=self), product_name)
            self.render_http_response(response)
        except:
            tb = traceback.format_exc()
            self.render_low_level_mistake(tb)


class Http404(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# get object or raise 404 not found
def get_object_or_404(TypeClass, id=None):
        try:
            data_model = TypeClass.get(TypeClass.id == id)
            return data_model
        except TypeClass.DoesNotExist:
            raise Http404("does not exist")

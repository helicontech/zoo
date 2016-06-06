# -*- coding: utf-8 -*-

from web.helpers.http import HttpResponse
import jinja2
from jinja2 import nodes
from jinja2.ext import Extension
from core.version import VERSION

# shortcut function rendering templates to http response object
def render_to_response(env: jinja2.Environment, template_filename: str, context: dict):
    template = env.get_template(template_filename)
    data = template.render(context)
    return HttpResponse(body=data)

# our change to django RequestContext
def request_context(request, context=None):
    if context is None:
        return {"zoo_version": VERSION}
    else:
        context["zoo_version"] = VERSION
        return context



class StaticPath(Extension):
    # a set of names that trigger the extension.
    tags = set(['static'])

    def __init__(self, environment):
        super(StaticPath, self).__init__(environment)
        # add the defaults to the environment
        environment.extend(
            static_path='',
        )

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # now we parse a single expression that is used as cache key.
        args = [parser.parse_expression()]
        # helper method on this extension.
        return self.call_method('_myfunc', args)

    def _myfunc(self, name):
        """Helper callback."""
        static_path = self.environment.static_path
        return static_path + name


class ReverseUrl(Extension):
    tags = set(['url'])

    def __init__(self, environment):
        super(ReverseUrl, self).__init__(environment)

        # add the defaults to the environment

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # now we parse a single expression that is used as cache key.
        args = [parser.parse_expression()]
        # helper method on this extension.

        return self.call_method('_myfunc', args)

        # return nodes.CallBlock(self.call_method('_cache_support', args),
        #                        [], [], body).set_lineno(lineno)

    def _myfunc(self, resolved_name):
        return resolved_name


class HandlebarsJS(Extension):
    tags = set(['handlebarsjs'])

    def __init__(self, environment):
        super(HandlebarsJS, self).__init__(environment)
        environment.extend(
            handlebarsjs_loader=None,
        )
        # add the defaults to the environment

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # now we parse a single expression that is used as cache key.
        args = [parser.parse_expression()]
        # helper method on this extension.
        return self.call_method('_myfunc', args)

    def _myfunc(self, resolved_name):
        file_content = self.environment.handlebarsjs_loader.get(resolved_name)
        output = (
            '<script type="text/x-handlebars-template" id="{name}">'
                '{content}'
            '</script>'
        )
        return output.format(name=resolved_name, content=file_content)

from os import listdir
from os.path import isfile, join

class HandlebarsJS_loader:

    def __init__(self, **kwargs):
        self.inner_dict = {}
        self.path = kwargs.get("path")
        self.ext = kwargs.get("extension")
        mypath = self.path

        # we work with only files without subdirectories
        for f in listdir(mypath):
            filename = join(mypath, f)
            if isfile(filename):
                with open(filename) as file:
                    data = file.read()
                    name = f.replace(self.ext, "")
                    self.inner_dict[name] = data

    # return file content associated with the name of template
    def get(self, name):
        return self.inner_dict[name]



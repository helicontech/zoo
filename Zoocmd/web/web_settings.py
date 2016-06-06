import jinja2
import web.helpers.template
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
import web.helpers.tmpl_context_function

# TODO move all definition from there
BASE_DIR = None
if getattr(sys, 'frozen', False):
        # The application is frozen
        BASE_DIR = os.path.dirname(sys.executable)
else:
        # The application is not frozen
        pathname = os.path.dirname(sys.argv[0])
        # Change this bit to match where you store your data files:
        BASE_DIR = pathname


TEMPLATE_LOADER = jinja2.FileSystemLoader([os.path.join(BASE_DIR,  "web", "zoo",  "templates"),
                                           os.path.join(BASE_DIR,  "web", 'zoo', 'jstemplates')])

STATIC_PATH = os.path.join(BASE_DIR,  "web", "zoo", "static")

template_environment = jinja2.Environment(loader=TEMPLATE_LOADER)
# url path to static
template_environment.static_path = "/static/"
template_environment.handlebarsjs_loader = web.helpers.template.HandlebarsJS_loader(path=os.path.join(BASE_DIR,
                                                                                                      "web",'zoo',
                                                                                                      'jstemplates'),
                                                                                    extension=".hbs")

template_environment.globals.update(static=web.helpers.tmpl_context_function.get_static,
                                    url=web.helpers.tmpl_context_function.reverse_url,
                                    handlebarsjs=web.helpers.tmpl_context_function.handlebarsjs_load
                                    )


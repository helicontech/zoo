import web.web_settings
import web.web_settings
from core.version import VERSION

def get_static(resolved_name):
    return web.web_settings.template_environment.static_path + resolved_name + "?version="+VERSION


__static_urls = {}
def tmpl_context_load_static(application_urls):
    if '___loaded' in __static_urls:
        return False
    for item in application_urls:
        (raw_string, module, dict_settings) = item
        new_str = raw_string.replace("$", "")
        __static_urls[dict_settings["name"]] = new_str


def reverse_url(resolved_name):
    if resolved_name in __static_urls:
        return  __static_urls[resolved_name]
    return ""

def handlebarsjs_load(resolved_name):
        file_content = web.web_settings.template_environment.handlebarsjs_loader.get(resolved_name)
        output = (
            '<script type="text/x-handlebars-template" id="{name}">'
                '{content}'
            '</script>'
        )
        return output.format(name=resolved_name, content=file_content)
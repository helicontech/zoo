# -*- coding: utf-8 -*-

from web.helpers.http import HttpResponseNotAllowed

from core.core import Core
from web.helpers.json import json_response, json_request


@json_response
def engine_list(request):
    """
    Получить список энжайнов.

    :param request:
    :return:
    """
    core = Core.get_instance()
    core.engine_storage.update()
    engines = core.engine_storage.feed.dump_products(core.engine_storage.feed.get_products())

    return engines


@json_response
def config(request, name):
    """
    GET - Получить конфиг для энажайна
    POST - сохранить конфиг для энажайна в engine_storage
    :param request:
    :param name:
    :return: :raise HttpResponseNotAllowed:
    """
    core = Core.get_instance()
    core.engine_storage.update()
    if request.method == 'GET':
        engine = core.engine_storage.feed.get_product(name)
        return engine.to_dict(True)

    if request.method == 'POST':
        engine_config = json_request(request)
        engine = core.engine_storage.feed.get_product(name)
        engine.config = engine_config
        core.engine_storage.feed.update_product(engine)
        core.engine_storage.save()
        return engine.to_dict(True)

    raise HttpResponseNotAllowed(['GET', 'POST'])



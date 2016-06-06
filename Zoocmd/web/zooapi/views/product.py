# -*- coding: utf-8 -*-

import urllib.parse

from core.core import Core
from web.helpers.json import json_response


@json_response
def product_list(request):
    """
    Получить список продуктов с учетом фильтров

    filter - тип продукта, product, application, engine
    installed - установлен или нет
    q - строка поиска
    :param request:
    :return:
    """
    product_filter = request.GET.get('filter', None)
    installed_filter = request.GET.get('installed', None)
    if installed_filter is not None:
        installed_filter = int(installed_filter)
    q = request.GET.get('q', None)
    core = Core.get_instance()
    core.update()
    if q:
        q = urllib.parse.unquote_plus(q)
        products = core.feed.dump_products(core.feed.search_products(q))
    else:
        products = core.feed.dump_products(core.feed.filter_products(product_filter, installed_filter))

    return products


@json_response
def product_id(request, prod_id):
    pass
# -*- coding: utf-8 -*-

from core.core import Core
from web.helpers.json import json_response


@json_response
def tag_list(request):
    """
    Хендлер. получить список тегов.
    с учетом фильра 'q' и типа продукта 'filter'
    :param request:
    :return:
    """
    product_filter = request.GET.get('filter', None)
    q = request.GET.get('q', None)
    core = Core.get_instance()
    if q:
        tags = core.feed.get_tags(core.feed.search_products(q))
    else:
        tags = core.feed.get_tags(core.feed.filter_products(product_filter))
    return tags




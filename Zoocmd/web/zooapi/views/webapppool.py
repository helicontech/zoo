# -*- coding: utf-8 -*-

from web.helpers.http import HttpResponseNotAllowed
import os
from core.core import Core
from web.helpers.json import json_response, json_request


@json_response
def pool_list(request):
    """
    Хендлер. Получить список пулов ииса
    :param request:
    :return:
    """
    core = Core.get_instance()
    if hasattr(core.api.os.web_server, 'APP_CMD') and os.path.exists(core.api.os.web_server.APP_CMD):
        pools = core.api.os.web_server.get_app_pool_list()
        return [pool.to_dict() for pool in pools]
    return []


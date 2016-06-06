# -*- coding: utf-8 -*-

from core.core import Core
from core.core_loader import CoreLoader
from web.helpers.json import json_response, json_request


@json_response
def settings(request):
    """
    Хендлер.
    GET - Получить настройки
    POST - сохранить переданные настройки, после сохранения настроек - перезагрузить ядро

    :param request:
    :return:
    """
    core = Core.get_instance()

    if request.method == 'POST':
        req = json_request(request)
        core.set_settings(req)
        # restart core
        setts = core.settings
        CoreLoader.get_instance().restart(setts)
    else:
        setts = core.settings

    return {
        'settings': setts.to_dict(),
        'info': setts.get_state()
    }


# -*- coding: utf-8 -*-


from core.core_loader import CoreLoader
from core.core import Core
from web.helpers.json import json_response


@json_response
def state(request):
    """
    Возвращает состояние загрузчика ядра.
    Используется на корневой странице для показать, прогресс загрузки ядра.
    """
    instance = CoreLoader.get_instance()
    state = instance.get_state()
    instance.clean_warnings()
    return state


@json_response
def has_upgrade(request):
    """
    Возвращает новую версию зу инсталера, на которую можно обновиться.
    """
    return {
        'version': Core.get_instance().has_upgrade() if Core.get_instance() else None
    }


@json_response
def cache(request):
    """
    Возвращает размер директории кеша.
    """
    return {
        'size': Core.get_instance().get_cache_size()
    }


@json_response
def cache_clear(request):
    """
    Очищает директорию кеша.
    """
    Core.get_instance().clear_cache()
    return {
        'size': Core.get_instance().get_cache_size()
    }


@json_response
def sync(request):
    Core.get_instance().set_expired(True)
    Core.get_instance().update()
    return {"status": True}


@json_response
def logs(request):
    """
    Возвращает размер директории логов.
    """
    return {
        'size': Core.get_instance().get_logs_size()
    }


@json_response
def logs_clear(request):
    """
    Очищает директорию логов.
    """
    Core.get_instance().clear_logs()
    return {
        'size': Core.get_instance().get_logs_size()
    }

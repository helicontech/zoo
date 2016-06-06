# -*- coding: utf-8 -*-

import json
import traceback
from web.helpers.http import HttpResponse, Http404
from core.helpers.common import json_encode, json_decode

def json_response_raw(func):
    """
    A decorator thats takes a view response and turns it
    into json.
    """
    def decorator(request, *args, **kwargs):
        http_status = 200
        headers = [("Content-Type", 'text/javascript'),
                   ('Cache-Control', 'no-cache,no-store,must-revalidate,max-age=0')]
        try:
            result = func(request, *args, **kwargs)
            # it's means that result is http response object or derived from it
            if hasattr(result, "status_code"):
                return result
        except Exception as ex:
            result = {
                'data': None,
                'error': {
                    'class': ex.__class__.__name__,
                    'args': '{0}'.format(ex),
                    'traceback': traceback.format_exc()
                }
            }
            http_status = 500
            traceback.print_exc()

        try:
            data = json_encode(result)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                response = HttpResponse(body=data, headers=headers, status_code=http_status)
                return response
        except Exception:
            raise
        response = HttpResponse(body=data, headers=headers, status_code=http_status)
        return response
    return decorator




def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        http_status = 200
        headers = [("Content-Type", 'text/javascript'),
                   ('Cache-Control', 'no-cache,no-store,must-revalidate,max-age=0')]
        try:
            result = func(request, *args, **kwargs)
            # it's means that result is http response object or derived from it
            if hasattr(result, "status_code"):
                return result
            result = {'data': result}

        except Exception as ex:
            result = {
                'data': None,
                'error': {
                    'print_traceback': not hasattr(ex, 'do_not_print'),
                    'class': ex.__class__.__name__,
                    'args': '{0}'.format(ex),
                    'traceback': traceback.format_exc()
                }
            }
            http_status = 500
            traceback.print_exc()

        try:
            data = json_encode(result)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                response = HttpResponse(body=data, headers=headers, status_code=http_status)
                return response
        except Exception:
            raise
        response = HttpResponse(body=data, headers=headers, status_code=http_status)
        return response
    return decorator


def json_request(request):
    """
    Парсит тело http-запроса из джейсона в питоньи объекты (словари и списки)
    """
    s = request.body
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return json_decode(s)

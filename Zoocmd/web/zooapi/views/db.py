# -*- coding: utf-8 -*-

from web.helpers.http import HttpResponseNotAllowed
import pymssql
import pymysql
import sqlite3

from web.helpers.json import json_response, json_request
from core.parameters_manager import KnownParameters


@json_response
def check(request):
    """
    Проверяет коннект к базы данных,
    используется на мастере установки приложения, если у приложения есть параметры для БД.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # распарсим джейсон запрос
    req = json_request(request)

    # и дёрнем соответствующий метод для полученного типа бд.
    if req[KnownParameters.DB_ENGINE.value] == "mysql":
        return test_mysql(
            req[KnownParameters.DB_HOST.value],
            req[KnownParameters.DB_PORT.value],
            req[KnownParameters.DB_USERNAME.value],
            req[KnownParameters.DB_PASSWORD.value],
            req[KnownParameters.DB_NAME.value])

    if req[KnownParameters.DB_ENGINE.value] == "mssql":
        return test_mssql(
            req[KnownParameters.DB_HOST.value],
            req[KnownParameters.DB_PORT.value],
            req[KnownParameters.DB_USERNAME.value],
            req[KnownParameters.DB_PASSWORD.value],
            req[KnownParameters.DB_NAME.value])

    if req[KnownParameters.DB_ENGINE.value] == "sqlite":
        return test_sqlite(
            req[KnownParameters.DB_NAME.value])

    return {'success': False, 'message': 'Unknown database engine: {0}'.format(req[KnownParameters.DB_ENGINE.value])}


def test_mysql(host, port, user, password, schema):
    """
    Тестирует коннект к БД Mysql по заданым параметрам
    """
    try:
        port = int(port)
        conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=schema)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        results = cur.fetchone()

        # Check if anything at all is returned
        if not results:
            return {'success': False, 'message': 'Connected successfully, but can\'t fetch records'}
        else:
            return {'success': True, 'message': 'Connected successfully'}

    except Exception as e:
        return {'success': False, 'message': str(e)}


def test_mssql(host, port, user, password, schema):
    """
    Тестирует коннект к БД MS SQL по заданым параметрам
    """
    try:
        port = int(port)
        conn = pymssql.connect(host=host, port=port, user=user, passwd=password, db=schema)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        results = cur.fetchone()

        # Check if anything at all is returned
        if not results:
            return {'success': False, 'message': 'Connected successfully, but can\'t fetch records'}
        else:
            return {'success': True, 'message': 'Connected successfully'}

    except Exception as e:
        return {'success': False, 'message': str(e)}


def test_sqlite(schema):
    """
    Тестирует коннект к БД Sqlite по заданым параметрам
    """
    try:
        conn = sqlite3.connect(schema)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        results = cur.fetchone()

        # Check if anything at all is returned
        if not results:
            return {'success': False, 'message': 'Connected successfully, but can\'t fetch records'}
        else:
            return {'success': True, 'message': 'Connected successfully'}

    except Exception as e:
        return {'success': False, 'message': str(e)}

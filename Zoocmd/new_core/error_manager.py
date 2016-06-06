# -*- coding: utf-8 -*-

import traceback


class ErrorManager(object):
    """
    Коллекция ошибок, которые случились во время создания ядра и загрузки фида.
    """

    def __init__(self):
        # внутрення коллекция
        self._coll = []

    def add(self, ex: Exception):
        """
        Добавить исключение.
        """
        self._coll.append((ex, traceback.format_exc()))

    def clear(self):
        """
        Очистить все ошибки.
        """
        self._coll.clear()

    def has_errors(self)-> bool:
        """
        Если ли ошибки?
        :return:
        """
        return len(self._coll) > 0

    def format_errors(self):
        """
        Возвращает список отформатированных ошибкок.
        """
        result = []
        for data in self._coll:
            ex = data[0]
            tb = data[1]
            result.append({
                'message': traceback.format_exception_only(ex.__class__, ex),
                'traceback': tb
            })

        return result

    def get_first(self):
        """
        Возвращает первую ошибку из коллекции.
        """
        if self._coll:
            return self._coll[0][0]
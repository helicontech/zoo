# -*- coding: utf-8 -*-

import traceback


class ErrorManager(object):
    """
    Коллекция ошибок, которые случились во время создания ядра и загрузки фида.
    """

    def __init__(self):
        # внутрення коллекция
        self._coll = []
        self._coll_non_critical = []

    def add(self, ex: Exception):
        """
        Добавить исключение.
        """
        self._coll.append((ex, traceback.format_exc()))

    def add_non_critical(self, ex: Exception):
        self._coll_non_critical.append((ex, traceback.format_exc()))

    def clear(self):
        """
        Очистить все ошибки.
        """
        self._coll.clear()
        self._coll_non_critical.clear()

    def has_errors(self)-> bool:
        """
        Если ли ошибки?
        :return:
        """
        return len(self._coll) > 0

    def has_warns(self)-> bool:
        """
        Если ли ошибки?
        :return:
        """
        return len(self._coll_non_critical) > 0

    def format_warns(self):
        """
        Возвращает список отформатированных ошибкок.
        """
        result = []
        for data in self._coll_non_critical:
            ex = data[0]
            tb = data[1]
            result.append({
                'message': traceback.format_exception_only(ex.__class__, ex),
                'traceback': tb
            })

        return result

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

    def get_first_warn(self):
        """
        Возвращает первую ошибку из коллекции.
        """
        if self._coll:
            return self._coll_non_critical[0][0]

    def get_first(self):
        """
        Возвращает первую ошибку из коллекции.
        """
        if self._coll:
            return self._coll[0][0]
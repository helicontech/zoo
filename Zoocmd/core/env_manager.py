# -*- coding: utf-8 -*-


class EnvManager(object):
    """
    Коллекция переменных окружения.
    """

    def __init__(self):
        # внутренне коллекция
        self.vars = dict()

    def expandvars(self, path: str):
        """
        Заменяет переменные окружения в пути на значения.

        """
        result = path

        if result:
            for (key, value) in self.vars.items():
                result = result.replace(key, value)

        return result

    def __setitem__(self, key, value):
        """
        Специальный метод для синтаксиса envs['key'] = 'value'
        """
        self.vars.__setitem__(key, value)

    def __getitem__(self, key):
        """
        Специальный метод для синтаксиса val = envs['key']
        """
        return self.vars.__getitem__(key)

    def __delitem__(self, key):
        """
        Специальный метод для синтаксиса del envs['key']
        """
        self.vars.__delitem__(key)
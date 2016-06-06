# -*- coding: utf-8 -*-

import re

from core.helpers.version import compare_versions


class VersionComparer(object):
    """
    Класс который умеет сравненать версии
    """

    # возможные операции сравнения
    ALLOWED_OPERATIONS = ('==', '>', '>=', '=>', '<', '<=', '=<')

    def __init__(self, operation, version):
        self.operation = operation
        self.version = version
        if not self.operation in self.ALLOWED_OPERATIONS:
            raise ValueError('Unexpected operation: {0} for {1}'.format(self.operation, self.version))

    def match(self, version)-> bool:
        """
        Сравнивает версию заданную в конструкторе с заданной в аргументе.
        """
        compare_result = compare_versions(version, self.version)

        if self.operation == '==':
            return compare_result == 0

        if self.operation == '<':
            return compare_result < 0

        if self.operation == '<=' or self.operation == '=<':
            return compare_result <= 0

        if self.operation == '>':
            return compare_result > 0

        if self.operation == '>=' or self.operation == '=>':
            return compare_result >= 0


class EntryComparer(object):
    """
    Класс, который умеет сравнивать имена с версией. Примеры:
    zoo==3
    zoo>3.0
    zoo<3.0,>4.0 <- bad
    zoo>3.0,<=5.0.0.1
    node==2.3
    mysql>=5.0,<5.6
    """

    RE_SPLIT_VERSION = re.compile(r'^([^,<>=-]+)(([=><]+)([\w.-]+)(,([=><]+)([\w.-]+))?)?$')

    def __init__(self, raw):
        raw = raw.lower()
        self.raw = raw
        self.vc1 = None
        self.vc2 = None

        # разбить входную строку на имя и версию
        m = self.RE_SPLIT_VERSION.match(raw)
        if m:
            self.name = m.group(1)
            if m.group(2):
                # первый оператор сравнения версии
                self.vc1 = VersionComparer(m.group(3), m.group(4))
                if m.group(5):
                    # второй оператор сравнения версии
                    self.vc2 = VersionComparer(m.group(6), m.group(7))
        else:
            raise ValueError('Unexpected version string: ' + raw)

    def match(self, name, version):
        """
        Сравнивает имя и версия с той, что задана в конструкторе.
        """
        if self.name != name.lower():
            # имена не равны
            return False

        if not version:
            # нет входной версии - равны
            return True

        if self.vc1:
            # первый оператор сравнения версии
            if not self.vc1.match(version):
                return False

        if self.vc2:
            # второй оператор сравнения версии
            if not self.vc2.match(version):
                return False

        return True

    def match_strict(self, name, version):
        """
        Сравнивает так же как и match(), но строже — версии должны точно совпасть.
        """
        if self.name != name.lower():
            return False

        if self.vc1:
            if not version:
                return False
            if not self.vc1.match(version):
                return False

        if self.vc2:
            if not version:
                return False
            if not self.vc2.match(version):
                return False

        # ok. all conditions matched
        return True

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.raw)


class ProductComparer(EntryComparer):
    pass


class OsComparer(EntryComparer):
    pass

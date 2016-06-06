# -*- coding: utf-8 -*-


class ProductParameter(object):
    """
    Represents product parameter used in product installation.
    ParametersManager creates and uses instances of this class.
    """

    def __init__(self, product_name, name, default=None):
        self.product_name = product_name
        self.name = name
        self.value = None
        self.default = default
        self.error = default is None
        self.has_set = False

    def __repr__(self):
        return "Parameter({0}, {1}, {2})".format(
            self.product_name,
            self.name,
            self.value
        )

    def set(self, value):
        self.value = value
        self.has_set = True
        self.error = False

    def get(self):
        return self.value

    def to_dict(self):
        """
        Representation that used in json serialization.
        """
        return {
            'name': self.name,
            'value': self.value or self.default,
            'default': self.default,
            'error': self.error
        }

    def query(self):
        """
        Queries parameter value when core is in interactive mode and ruuning in cmd line.
        """
        prompt = '{0}: {1}{2}: '.format(
            self.product_name,
            self.name.replace('_', ' ').capitalize(),
            ' (default: {0})'.format(self.default) if self.default else ''
        )
        value = input(prompt)
        if not value:
            value = self.default
        self.set(value)


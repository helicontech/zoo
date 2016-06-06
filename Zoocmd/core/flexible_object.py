# -*- coding: utf-8 -*-

class FlexibleObject(object):

    def __init__(self, **data):
        static_attrs = data.get('static_attrs', [])
        super(FlexibleObject, self).__setattr__('__static_attrs', static_attrs)
        flexible_data = {}

        if len(static_attrs)>0:
            del data['static_attrs']

        for key in data:
            if key in static_attrs:
                super(FlexibleObject, self).__setattr__(key, data[key])
            else:
                flexible_data[key] = data[key]

        super(FlexibleObject, self).__setattr__('data', flexible_data)

    def __setattr__(self, k, v):
        if k in self.__dict__['__static_attrs']:
            self.__dict__[k] = v
        else:
            self.__dict__['data'][k] = v

    def __getattr__(self, k):
        # we don't need a special call to super here because getattr is only
        # called when an attribute is NOT found in the instance's dictionary
        if k in self.data:
            return self.data[k]
        else:
            raise AttributeError

    def __delattr__(self, name):
        if name in self.__dict__['__static_attrs'] and name in self.__dict__:
            del self.__dict__[name]
            return True

        if name in self.data:
            del self.data[name]
            return True

        raise AttributeError


class NewObject(FlexibleObject):

    def __init__(self, **data):
        static_methods = ['a', 'b', 'c']
        data["static_attrs"] = static_methods
        super(NewObject, self).__init__(**data)

    def test_method(self):
        print("test method")

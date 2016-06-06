# -*- coding: utf-8 -*-

from collections import OrderedDict
import yaml
import os
from core.models.product import Product
from core.models.application import Application
from core.models.engine import Engine
from core.helpers.yaml_literal import Literal
from core.helpers.yaml_loader import literal_representer, product_representer, ordered_dict_representer, YamlLoader
from core.models.file import File


"""
Implements helper to save yaml and yaml representers for core classes.
"""

_representers_added = False
if not _representers_added:
    # add process-wide yaml representers for core classes
    yaml.add_representer(Literal, literal_representer, yaml.SafeDumper)
    # representer for BaseProduct is not working!
    yaml.add_representer(Product, product_representer, yaml.SafeDumper)
    yaml.add_representer(Application, product_representer, yaml.SafeDumper)
    yaml.add_representer(Engine, product_representer, yaml.SafeDumper)
    yaml.add_representer(File, product_representer, yaml.SafeDumper)
    yaml.add_representer(OrderedDict, ordered_dict_representer, yaml.SafeDumper)
    _representers_added = True


class YamlHelper(object):
    """
    Helper class for saving data to yaml file
    """

    @staticmethod
    def save(data, path):
        """
        Dumps 'data' object to yaml string and saves to specified path.
        """
        with open(path, 'wb') as f:
            stream = YamlHelper.dump_to_string(data)
            if isinstance(data, list):
                # add new lines for top level items of list (used for engines.yaml, install-history.yaml)
                f.write(stream.replace(b'\n- ', b'\n\n\n- '))
            else:
                f.write(stream)

    @staticmethod
    def dump_to_string(data)-> str:
        """
        Dumps 'data' object to yaml string
        """
        result = yaml.safe_dump(data,
                                default_flow_style=False,
                                default_style=None,
                                encoding='utf-8',
                                allow_unicode=True,
                                explicit_start=None)
        return result


    @staticmethod
    def load_from_file(filename: str)-> OrderedDict:
        data = None
        if os.path.exists(filename):
            data = yaml.load(open(filename, 'r'), YamlLoader)

        return data



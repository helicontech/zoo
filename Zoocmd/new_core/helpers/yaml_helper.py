"""
Copyright © Helicon Tech. All rights reserved.

Implements helper to save yaml and yaml representers for core classes.
"""

from collections import OrderedDict
import yaml

from core.models.product import Product
from core.models.application import Application
from core.models.engine import Engine
from core.models.file import File



class Literal(str):
    """Dumb class for yaml representer"""
    pass



class YamlLoader(yaml.Loader):
    """
    Custom yaml loader.
    The main task: construct OrderedDict instead dict for yaml map data type.
    """
    def __init__(self, stream):
        super(YamlLoader, self).__init__(stream)
        # add custom constructors
        self.add_constructor('tag:yaml.org,2002:map', YamlLoader.construct_yaml_map)
        self.add_constructor('tag:yaml.org,2002:omap', YamlLoader.construct_yaml_map)

    def construct_yaml_map(self, node):
        """
        Constructs OrderedDict for yaml map.
        :param node:
        :return:
        """
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        """
        Helper to create OrderedDict for yaml node.
        """
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None, 'expected a mapping node, but found %s' % node.id,
                                                    node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping', node.start_mark,
                                                        'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def literal_representer(dumper, data):
    """
    Returns dumper for Literals with '|' style.
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


def product_representer(dumper, data):
    """
    Returns dumper for BaseProduct object as dict.
    """
    return dumper.represent_yaml_object('tag:yaml.org,2002:map', data, None)


def ordered_dict_representer(dumper, data):
    """
    Represents OrderedDict for yaml dumper.
    """
    values = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)
        values.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', values)



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


def save_yaml(data, path):
    """
    Dumps 'data' object to yaml string and saves to specified path.
    """
    with open(path, 'w') as f:
        stream = dump_to_string(data)
        if isinstance(data, list):
            # add new lines for top level items of list (used for engines.yaml, install-history.yaml)
            f.write(stream.replace('\n- ', '\n\n\n- '))
        else:
            f.write(stream)

def dump_to_string(data)-> str:
    """
    Dumps 'data' object to yaml string
    """
    result = yaml.safe_dump(data,
                            default_flow_style=False,
                            default_style=None,
                            explicit_start=None)
    return result



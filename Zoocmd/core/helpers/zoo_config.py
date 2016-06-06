import os
import yaml
from core.helpers import yaml_loader
from yaml.scanner import ScannerError


def get_zoo_config(physical_path)-> dict:
    """
    Loads zoo app config from 'physical_path' and returns ready-to-use dict object with config.
    """
    data = None
    if os.path.exists(physical_path):
        data = yaml.load(open(physical_path, 'r'), yaml_loader.YamlLoader)

    return data


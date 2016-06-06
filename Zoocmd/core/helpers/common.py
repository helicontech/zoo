# -*- coding: utf-8 -*-

"""
Common useful helpers
"""
import json
import collections
import os
from datetime import datetime
import re
import psutil

def kill_proc_tree(pid, including_parent=True):
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        psutil.wait_procs(children, timeout=5)
        if including_parent:
            parent.kill()
            parent.wait(5)

def str_timestamp_to_datetime(s):
    f = float(s)
    f += 0.0000005
    result = datetime.fromtimestamp(f)
    return result

# DEPRECATED
def expand_variables_in_dict(custom_env, envs):
        """
        развернуть переменные окружения в словаре для каждого значения
         - сначала системные
         - затем зу
        :param envs:
        :return:
        """
        result = dict()
        for (key, value) in envs.items():
            key = str(key)
            value = str(value)
            try:
                result[key.upper()] = os.path.expandvars(envs[key])
                result[key.upper()] = expand_zoo_variables(custom_env, envs[key])
            except:
                logging.info("trouble expand_zoo_variables > {0} --> {1}".format(key, value))
                result[key.upper()] = value


        return result

def expand_zoo_variables(custom_env, string_to_process):
        """
        развернуть в строке переменные окружения zoo
        поискать в строке '%KEY%' если есть то заменить на соответсвующее значение из словаря
        и так для каждого ключа в словаре

        :param string_to_process:
        :return:
        """


        result = string_to_process
        Accum = ""
        for i in re.finditer("%([^%]+)%", string_to_process):
            env_key = i.group(1)
            to_replace = i.group(0)
            if env_key in custom_env:
                value = custom_env[env_key]
                result = result.replace(to_replace, value)

        return result

def json_encode(obj: dict) -> str:
    return json.dumps(obj, indent=1)


def json_decode_file(filename: str):

    with open(filename) as data_file:
        body = data_file.read()
        return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(body)
    return None

def json_decode(body: str):
    return json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(body)

def is_local_file(path):
    """
    Check that specified path is local, not URL.
    """
    if path.lower().startswith("http://"):
        return False
    if path.lower().startswith("https://"):
        return False
    if path.lower().startswith("ftp://"):
        return False

    return True

import logging

# not USED
def expand_env_variables(self, env, string_to_process):
        """
        развернуть в строке переменные окружения zoo
        поискать в строке '%KEY%' если есть то заменить на соответсвующее значение из словаря
        и так для каждого ключа в словаре

        :param string_to_process:
        :return:
        """
        result = string_to_process
        for (key, value) in env.items():
            if string_to_process.lower() != key.lower():
                result = result.lower().replace("%" + key.lower() + "%", value)

        if result.lower().find("%") != -1:
            #repeat if nested expand needed
            for (key, value) in env.items():
                if string_to_process.lower() != key.lower():
                    result = result.lower().replace("%" + key.lower() + "%", value)


        if result.lower() != string_to_process.lower():
            logging.debug("expand_zoo_variables > {0} --> {1}".format( string_to_process, result.lower()))
        return result.lower()

def object_attrs_to_dict(obj: object, attrs: list) -> dict:
    """
    Returns dict with keys specified in 'attr' with values from 'obj' object.
    Example: object_attrs_to_dict(obj, ['a', 'b']) -> {'a': 'a value', 'b': 'b value'}
    """
    result = {}
    for attr in attrs:
        result[attr] = obj.__dict__[attr]
    return result


def str_list_to_dict(pairs_list):
    """
    Parses strings from list formatted as 'k1=v1' to dict with keys 'k1', 'v1'.
    Example: str_list_to_dict(['k=v', 'a=b']) —> {'k':'v', 'a': 'b'}
    :param pairs_list: list of strings
    :return: dict with parsed keys/values
    """
    result = {}
    for l in pairs_list:
        ar = l.split("=")
        result[ar[0]] = ar[1]

    return result


def search_dict_in_list_by_attr(items: list, attr_name, attr_value):
    for item in items:
        if item.get(attr_name) == attr_value:
            return item
    return None

def get_from_list_by_attr(items: list, attr_name):
    for item in items:
        attr_value = item.get(attr_name, False)
        if attr_value:
            return item
    return None
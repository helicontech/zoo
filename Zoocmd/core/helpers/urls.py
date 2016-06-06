# -*- coding: utf-8 -*-

"""
Implements of URLs manipulation.
"""


def remove_starting_backward_slash(value: str):
    """
    Removes backward slash at the begin of string.
    """
    if value.startswith('\\'):
        return value[1:]
    return value


def add_trailing_slash(value):
    """
    Add slash to the end of string if needed.
    """
    result = value
    if not value.endswith("/"):
        result = value + "/"
    return result


def remove_starting_forward_slash(value):
    """
    Removes forward slash at the begin of string.
    """
    result = value
    if value.startswith("/"):
        result = value[1:]
    return result


def combine_virtual_path(p1: str, p2: str)-> str:
    """
    Joins two virtual paths.
    """
    tail = add_trailing_slash(p2)
    tail = remove_starting_forward_slash(tail)
    return add_trailing_slash(p1) + tail


# -*- coding: utf-8 -*-

import logging
from core.helpers.distutil_version import LooseVersion


def compare_versions(v1: str, v2: str)-> int:
    """
    Compares version strings formatted as '1.2.3.4'.
    :param v1:
    :param v2:
    :return: -1 if less, 0 if equals, 1 if greater
    """
    try:
        return LooseVersion(v1.lower())._cmp(LooseVersion(v2.lower()))
    except Exception as e:
        logging.error("Can't compare versions: '{0}' '{1}'".format(v1, v2))
        raise e

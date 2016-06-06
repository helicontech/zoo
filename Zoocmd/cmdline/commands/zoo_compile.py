# -*- coding: utf-8 -*-

import argparse
import os
import shutil
import sys
import yaml
import codecs
from core.helpers.yaml_literal import Literal
from core.helpers import yaml_loader
from core.helpers.common import is_local_file
from core.helpers.yaml_helper import YamlHelper

"""
Feed compiler.
Input: 'source' folder with bunch of yaml and installer files.
Result: 'destination' folder single yaml file and folder tree with installer files, icons etc.
"""

def write_all(full_path, content):
    """
    Write file.
    :param full_path: file full path
    :param content: content to write
    """
    with open(full_path, 'wb') as content_file:
        content_file.write(content)


def parse_yaml(full_path):
    """
    Loads file
    :param full_path:file full path
    :rtype : Python object (dict) from yaml file
    """
    with codecs.open(full_path, 'r', 'utf-8') as stream:
        data = yaml.load(stream, yaml_loader.YamlLoader)
    return data


def process_yaml(full_path, data: dict, src, dest):
    """
    Processes icon and file link in yaml object.
    :param full_path: file full path
    :param data: yaml object
    :param src: source folder
    :param dest: destination folder
    """
    for product in data:
        # icon attr
        if "icon" in product:
            product["icon"] = _patch(full_path, product["icon"], src, dest)

        if "description" in product:
            product["description"] = Literal(product["description"])

        if "find_installed_command" in product:
            product["find_installed_command"] = Literal(product["find_installed_command"])

        if "install_command" in product:
            product["install_command"] = Literal(product["install_command"])

        if "uninstall_command" in product:
            product["uninstall_command"] = Literal(product["uninstall_command"])

        if "upgrade_command" in product:
            product["upgrade_command"] = Literal(product["upgrade_command"])

        # files list
        if "files" in product:
            if product["files"] is None:
                continue
            for file in product["files"]:
                path = file["file"]
                if is_local_file(path):
                    # path path for local (in 'source') files, not hyperlinks
                    file["file"] = _patch(full_path, file["file"], src, dest)


def _patch(full_path, path, src, dest):
    """
    Patches file path to relative path in destination folder.
    :param full_path:
    :param path:
    :param src:
    :param dest:
    :return: relative file path in destination folder
    """

    # source yaml file directory
    yaml_dir = os.path.dirname(full_path)
    # full file path
    file_full_path = os.path.join(yaml_dir, path)
    # break if file does not exists
    if not os.path.exists(file_full_path):
        raise Exception("Error in yaml '{0}'. source file '{1}' not found".format(full_path, path))

    print("processing '{0}'".format(yaml_dir))

    # relative path in destination folder
    file_rel_path = os.path.relpath(file_full_path, src)
    # full path in destination folder
    file_dest = os.path.join(dest, file_rel_path)
    # directory path
    dir_dest = os.path.dirname(file_dest)
    # create directory if not exists
    if not os.path.exists(dir_dest):
        os.makedirs(dir_dest)

    print("copy '{0}' --> '{1}'".format(path, file_dest))
    # copy file to destination
    shutil.copy(file_full_path, dir_dest)

    return file_rel_path


def make_build(args):
    """
    пройтись рекурсивно по всем каталогам
    распарсить ямл
    найти ссылки на файлы
    скпоировать файлы
    подправить ссылки
    добавить в большой ямл
    """

    output = [b"# zoo feed version 1.0\n"]

    # recursive walk in source folder
    for root, dirs, files in os.walk(args[0]):
        for f in files:
            # skip non-yaml files
            if not f.lower().endswith(".yaml"):
                continue

            # skip. files
            if f.lower().startswith("."):
                continue


            full_path = os.path.join(root, f)
            # load yaml
            data = parse_yaml(full_path)
            # process loaded yaml
            process_yaml(full_path, data, args[0], args[1])
            # save processed yaml to string
            dumped_yaml = YamlHelper.dump_to_string(data)
            output.append(dumped_yaml)

    # save to result file
    result_path = os.path.join(args[1], "feed.yaml")
    write_all(result_path, b''.join(output))


def main():
    """
    Compiler entry point
    """

    # parse cmd line args
    parser = create_parser()
    print(sys.argv)
    args = parser.parse_args()

    # print help if no args
    if len(sys.argv) <= 1:
        parser.print_help()
        return

    # compile!
    make_build(args)


if __name__ == '__main__':
    main()
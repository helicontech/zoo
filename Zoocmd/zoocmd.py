# -*- coding: utf-8 -*-
import time
import sys

from core.settings import Settings

from cmdline import argument_parser
from cmdline.route import process_commands

"""
Main function of cmd line interface
"""

def main():
    """
    Main entry point of cmd line interface
    """

    # parse cmd line arguments



    parser = argument_parser.create_parser()
    args = parser.parse_args()



    settings = Settings.load_from_file(args.settings)
    # insert default feed for Zoo
    # if not args, just print help
    if len(sys.argv) <= 1:
        parser.print_help()
        return

    # load settings from settings.yaml
    # print("encoding %s" % sys.getdefaultencoding())
    # sys.setdefaultencoding("utf-8")
    # if additional feed urls are in cmd line args, then add it to settings
    if args.urls:
        local_list = args.urls
        settings.urls.extend(local_list)

    # route commands
    process_commands(args, settings)

if sys.platform.startswith('win'):
    import win32console
    oldCodePage = win32console.GetConsoleOutputCP()
    win32console.SetConsoleOutputCP(65001)

main()

try:
    if oldCodePage:
        win32console.SetConsoleOutputCP(oldCodePage)
except NameError:
    pass
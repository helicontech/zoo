# -*- coding: utf-8 -*-

import argparse

"""Description of arguments of command line interface"""


def create_parser():
    """Create command line arguments parser"""
    parser = argparse.ArgumentParser(description='Helicon Zoo command line')

    # print settings from settings.yaml
    parser.add_argument('--get-settings', action='store_true', help='get current settings')

    # write settings to settings.yaml
    parser.add_argument('--set-settings', dest="set_settings", nargs="+", help='set settings')

    # set urls of additional feeds
    parser.add_argument('--feed-urls', dest='urls', nargs='*', default='', help='feed urls to load')

    # print installed products
    parser.add_argument('--list-installed', action='store_true', dest='show_installed',
                        help='show all installed programs')

    # print installed products
    parser.add_argument('--run-tests', action='store_true', dest='run_test',
                        help='run tests over software')

    # print all products
    parser.add_argument('--list', action='store_true', dest='list_products',
                        help='list latest versions of all available products')

    # custom settings path
    parser.add_argument('--settings', dest='settings', default=None, help='search the settings in custom directory')

    # custom data dir
    parser.add_argument('--data-dir', dest='data_dir', default=None, help='default data directory')

    # search products
    parser.add_argument('--search', dest='search', help='search products for name and descriptions')

    # search installed products and write they to current.yaml
    parser.add_argument('--sync', action='store_true', dest='sync', help='synchronize installed version of products from system')

    # set products to install pr uninstall
    parser.add_argument('--products', dest='products', nargs="*", help='product names to install/uninstall')

    # make intstall
    parser.add_argument('--install', dest='install', action='store_true', help='install of specified products')

    # set install parameters for products to install
    parser.add_argument('--parameters', dest='parameters', nargs="?", help="application install parameters\n\
    Format: --parameters param1=val1 product2@param2=val2 ...")

    # set install parameters for products to install
    parser.add_argument('-pj', '--data-parameters-json',
                        dest='json_params',
                        nargs="?",
                        help="install with  parameters in file json format")

    # set install parameters for products to install
    parser.add_argument('-py', '--data-parameters',
                        dest='yml_params',
                        nargs="?",
                        help="install with  parameters in file yaml format")



    # make uninstall
    parser.add_argument('--uninstall', action='store_true', dest='uninstall', help='uninstall a program')

    # quit mode
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False,
                        help='don\'t print anything to stdout')
    # allow communicate with user during install process
    parser.add_argument('-i', '--interactive', action='store_true', dest='interactive', default=False,
                        help='allow to ask install parameters if needed')
    # ignore any errors
    parser.add_argument('-f', '--force', action='store_true', dest='force', default=False, help='ignore exit code')

    # set log level
    parser.add_argument('--log-level', dest='log_level', default=None,
                        help='set log level (debug, warning, info, error, critical)')

    # start ui web server
    parser.add_argument('--run-server', dest='run_server', action='store_true', help='run web ui at http://localhost:7799/')

    # set ui server port
    parser.add_argument('--run-server-addr', dest='run_server_addr', default='7799', help='bind web ui server to "addr:port" or port')

    # start install/unstall task
    parser.add_argument('--start-install-worker', dest='worker_task_id', type=int, help='start supervisour worker')

    parser.add_argument('-l', '--task-log', dest='task_log',
                        nargs="?", default=None,
                        help='specify log for task if not specified will print to stdout')

    parser.add_argument('--task-work', dest='task_id', type=int, help='start installer worker with task by id')







    # compile zoo feed from dest  to src
    parser.add_argument('--compile-repository', nargs=2, dest="zoo_compile",
                        help='compile zoo feed, first agrument   src feed directory, second destination feed ')


    return parser



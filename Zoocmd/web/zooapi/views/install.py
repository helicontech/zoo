# -*- coding: utf-8 -*-

from web.helpers.http import HttpResponseNotAllowed

from core.core import Core
from core.product_collection import ProductCollection
from core.dependency_manager import DependencyManager
from core.parameters_manager import ParametersManager
from core.parameters_parser import ParametersParserJson
from core.task_manager import TaskManager, TaskFactory
from web.taskqueue.tornado_worker import TornadoWorker


from web.helpers.json import json_response, json_request


# пример ответа с деревом зависимостей
example_initial_response = """
- product:
    name: Wordpress
    title: Wordpress
  and:
  - or:
    - product:
        name: PHP54Engine
        title: PHP54Engine
      and:
      - product:
          name: PHP54
          title: PHP54
      - product:
          name: ZooIISModule
          title: ZooIISModule
    - product:
        name: PHP55Engine
        title: PHP55Engine
      and:
      - product:
          name: PHP55
          title: PHP55
        and:
        - product:
            name: WinCache
            title: WinCache
      - product:
          name: ZooIISModule
          title: ZooIISModule
  - or:
    - product:
        name: Mysql
        title: Mysql
    - product:
        name: Postgres
        title: Postgres
  - product:
      name: WordpressTheme
      title: WordpressTheme
- product:
    name: Ghost
    title: Ghost
  and:
  - product:
      name: Nodejs
      title: Nodejs
  - product:
      name: ZooIISModule
      title: ZooIISModule
"""

@json_response
def install_application(request, app_name):
    """
    Этот вызов используется для передать в веб-интерфейс дерево зависимостей
    для первого шага install application
    Возвращает продукты необходимые для установки Application
    для запуска инсталяции используется стандартный вызов install
    Примеры запросов и ответов:

    начальный запрос:
    """


    req = json_request(request)
    # это начальный запрос?
    dm = DependencyManager()
    core = Core.get_instance()
    # продукты, которые запрошены на установку (без зависимостей)
    requested_products = [app_name]
    if len(requested_products) > 1:
        raise RuntimeError("You are able to install only one application")
    application_item = [dm.get_dependencies(product_name) for product_name in requested_products]
    resp = {'task': None,
            "state": "requirements",
            'items': application_item}
    return resp

@json_response
def install(request):

    """
    Этот вызов используется для передать в веб-интерфейс дерево зависимостей
    и принять от него запрос на установку.
    Примеры запросов и ответов:

    начальный запрос:
    command: "start"
    requested_products: [JavaJettyTemplate]

    ответ:
    task:
      id: 168
      url: /task/168/
    items:
      paramters: [...]
      product:
        name: ...
        title: ...
      and:
      - item 1...
      - item 2...
    """
    # TODO do not give ability to install application through this function
    if request.method != 'POST':
        # принимаем только пост-запросы
        resp = HttpResponseNotAllowed(['POST'])
        return resp

    # джейсон запрос в питоний словарь
    req = json_request(request)
    # это начальный запрос?
    dm = DependencyManager()
    core = Core.get_instance()

    # продукты, которые запрошены на установку (без зависимостей)
    requested_products = req['requested_products']

    if req["command"] == "start":
        # если это начальный запрос, то отдаем дерево зависимостей
        resp = {
            'task': None,
            "state": "requirements",
            'items': [dm.get_dependencies(product_name) for product_name in requested_products]
        }
    else:
        # это запрос на установку
        # список имён продуктов, которые нужно установить
        # ВАЖНЫЙ МОМЕНТ (с зависимостями)
        product_list = [item['product'] for item in req['install_products']]
        # переворачиваем его
        product_list.reverse()
        # добывает спсисоко продуктов из списка имён
        products = ProductCollection(product_list, feeds=(core.feed, core.current))
        # парсим параметры установки из запроса
        parsed_parameters = ParametersParserJson(req['install_products']).get()
        # создаём менеджер параметров
        parameter_manager = ParametersManager(core, products, parsed_parameters)
        # все ли параметры заполнены?
        if parameter_manager.are_all_parameters_filled():
            # всё ок, создаём задание на установку
            task = TaskFactory.create_task("install", products, parameter_manager)
            task_id = TaskManager.queue_task(task)
            TornadoWorker.start_new_task(task)
            # и готовим ответ веб-интерфейсу, что уставнока началась
            resp = {
                'task': {
                    'id': task_id,
                },
            }
        else:
            # что-то не так с параметрами, возвращаем в веб морду ошибку
            resp = {
                'task': None,
                'items': [dm.get_dependencies(product_name) for product_name in req['requested_products']],
                'error': [parameter_manager.get_error(product) for product in products]
            }

    return resp


@json_response
def upgrade(request):
    """
    Обрабатывает запросы на апгрейд продуктов.
    Форматы входных запросов и выходных ответов такие же как для install()
    """
    if request.method != 'POST':
        # принимаем только пост-запросы
        return HttpResponseNotAllowed(['POST'])

    # парсим джейсон запрос
    req = json_request(request)
    initial = 'initial' in req
    dm = DependencyManager()
    requested_products = req['requested_products']
    core = Core.get_instance()
    if initial:
        # если это начальный запрос, то отдаем дерево зависимостей
        resp = {
            'task': None,
            'items': [dm.get_dependencies(product_name) for product_name in requested_products]
        }
    else:
        # это запрос на апгрейд
        # список имён продуктов, которые нужно апгрейдить (с зависимостями)
        product_list = [item['product'] for item in req['install_products']]
        product_list.reverse()
        # добывает спсисоко продуктов из списка имён
        products = ProductCollection(product_list)
        parsed_parameters = ParametersParserJson(req['install_products']).get()
        # создаём менеджер параметров
        parameter_manager = ParametersManager(core, products, parsed_parameters)
        # создаёт задачу на апгрейд
        task = TaskFactory.create_task("upgrade", products, parameter_manager)
        task_id = TaskManager.queue_task(task)
        TornadoWorker.start_new_task(task)
        resp = {
            'task': {
                'id': task_id,
            },
            'items': None
        }

    return resp


@json_response
def uninstall(request):
    """
    Обрабатывает запросы на деинсталляцию продуктов.

    """

    if request.method != 'POST':
        # принимаем только пост-запросы
        return HttpResponseNotAllowed(['POST'])

    # парсим джейсон запрос
    req = json_request(request)
    # это начальный запрос ?
    # список имён продуктов для деинсталляции
    requested_products = req['requested_products']
    # добываем список продуктов из списка имён
    products = ProductCollection(
        [product_name for product_name in requested_products],
        feed=Core.get_instance().current_storage.feed,
        # feed=Core.get_instance().feed,
        fail_on_product_not_found=False)

    if req["command"] == "start":
        # для начального запроса отдает список продуктов
        resp = {
            'task': None,
            'state': 'product_list',
            'items': [
                {
                    'product': product.to_dict(True),
                    'parameters': [],
                    'error': None
                }
                for product in products
            ]
        }
    else:
        # создаём задачу на деинсталляцию
        task = TaskFactory.create_task("uninstall", products)
        task_id = TaskManager.queue_task(task)
        TornadoWorker.start_new_task(task)
        # и готовим ответ веб-интерфейсу, что уставнока началась
        resp = {'task': {'id': task_id},
                "state": "uninstalling"}


    return resp

from web.zooapi.views.product import product_list, product_id
from web.zooapi.views.tag import tag_list
from web.zooapi.views.website import website_list, server_root, website_item, website_path,\
    website_create, website_launch, check_webserver_installed
from web.zooapi.views.engine import engine_list, config
from web.zooapi.views.webapppool import pool_list
from web.zooapi.views.install import install, uninstall, upgrade, install_application
from web.zooapi.views.task import task_list, task, rerun, cancel_task, log, task_paging
from web.zooapi.views.console import create, cancel, read, write
from web.zooapi.views.db import check
from web.zooapi.views.settings import settings
from web.zooapi.views.core import state, logs_clear, logs, cache, cache_clear, has_upgrade, sync
from web.helpers.http import CommonRequestHandler, CommonRequestHandlerOneParam
from web.helpers.http import CommonRequestHandlerTwoParam, SettingsRequestHandler



"""
REST API.
Описание урлов и хендлеров для них.
"""
application_urls = [
   (r'/api/2/product/list/$', CommonRequestHandler,
    dict(callable_object=product_list, name='zooapi.views.product.product_list', appname='api')),
   (r'/api/2/product/id/(?P<prod_id>[\w\.]+)/$', CommonRequestHandlerOneParam,
    dict(callable_object=website_create, name='zooapi.views.product.product_id', appname='api')),
   # спсико тегов
   (r'/api/2/tag/list/$', CommonRequestHandler,
    dict(callable_object=tag_list, name='zooapi.views.tag.tag_list', appname='api')),
   # список сайтов для страницы инсталляции не переопределяем его
   (r'/api/2/server/list/$', CommonRequestHandler,
    dict(callable_object=website_list, name='zooapi.views.website.website_list', appname='api')),
   # создать web site
   (r'/api/2/server/create/$', CommonRequestHandler,
    dict(callable_object=website_create, name='zooapi.views.website.website_create', appname='api')),
   # список сайтов для дерева сервера
   (r'/api/2/server/root/$', CommonRequestHandler,
    dict(callable_object=server_root, name='zooapi.views.website.server_root', appname='api')),
   # список узлов внутри сайта
   (r'/api/2/server/root/(?P<param1>[^/]+)/$', CommonRequestHandlerOneParam,
    dict(callable_object=website_item, name='zooapi.views.website.website_item', appname='api')),
   # список узлов в поддиректориях сайта
   (r'/api/2/server/root/(?P<param1>[^/]+)(?P<param2>/.*)?$', CommonRequestHandlerTwoParam,
    dict(callable_object=website_path, name='zooapi.views.website.website_path', appname='api')),
   # спсиков энжинов
   (r'/api/2/engine/list/$', CommonRequestHandler,
    dict(callable_object=engine_list, name='zooapi.views.engine.engine_list', appname='api')),

   (r'/api/2/site_launch/$', CommonRequestHandler,
    dict(callable_object=website_launch, name='zooapi.views.website.website_launch', appname='api')),

   (r'/api/2/check_webserver_installed/$', CommonRequestHandler,
    dict(callable_object=check_webserver_installed,
         name='zooapi.views.website.check_webserver_installed', appname='api')),

   # конфиг для энжина
   (r'/api/2/engine/id/(?P<param1>[^/]+)/config/$', CommonRequestHandlerOneParam,
    dict(callable_object=config, name='zooapi.views.engine.config', appname='api')),
   # спсиок пуллов IIS
   (r'/api/2/webapppool/list/$', CommonRequestHandler,
    dict(callable_object=pool_list, name='zooapi.views.webapppool.pool_list', appname='api')),
   # инсталляция продуктов
   (r'/api/2/install/application/(?P<param1>[\w\.]+)$', CommonRequestHandlerOneParam,
    dict(callable_object=install_application, name='zooapi.views.install.install_application', appname='api')),
   # install api
   (r'/api/2/install/$', CommonRequestHandler,
    dict(callable_object=install, name='zooapi.views.install.install', appname='api')),
   # апгрейд
   (r'/api/2/upgrade/$', CommonRequestHandler,
    dict(callable_object=upgrade, name='zooapi.views.install.upgrade', appname='api')),
   # деинсталляция
   (r'/api/2/uninstall/$', CommonRequestHandler,
    dict(callable_object=uninstall, name='zooapi.views.install.uninstall', appname='api')),
   # спсиок задач
   (r'/api/2/task/list/$', CommonRequestHandler,
    dict(callable_object=task_list, name='zooapi.views.task.task_list', appname='api')),
    # спсиок задач
   (r'/api/2/task_paging/list/$', CommonRequestHandler,
    dict(callable_object=task_paging, name='zooapi.views.task.task_paging', appname='api')),

   # отменить задачу
   (r'/api/2/task/id/(?P<param1>[\w\.]+)/cancel/$', CommonRequestHandlerOneParam,
    dict(callable_object=cancel_task, name='zooapi.views.task.cancel', appname='api')),
   # перезапустить задачу
   (r'/api/2/task/id/(?P<param1>[\w\.]+)/rerun/$', CommonRequestHandlerOneParam,
    dict(callable_object=rerun, name='zooapi.views.task.rerun', appname='api')),
   # вренуть логи задачи
   (r'/api/2/task/id/(?P<param1>[\w\.]+)/log/$', CommonRequestHandlerOneParam,
    dict(callable_object=log, name='zooapi.views.task.log', appname='api')),
    # получить детали задачи
   (r'/api/2/task/id/(?P<param1>[\w\.]+)/$', CommonRequestHandlerOneParam,
    dict(callable_object=task, name='zooapi.views.task.task', appname='api')),
   # создать консоль
   (r'/api/2/console/create/$', CommonRequestHandler,
    dict(callable_object=create, name='zooapi.views.console.create', appname='api')),
   # получить выхлоп из консоли
   (r'/api/2/console/read/$', CommonRequestHandler,
    dict(callable_object=read, name='zooapi.views.console.read', appname='api')),
   # написать в консоль
   (r'/api/2/console/write/$', CommonRequestHandler,
    dict(callable_object=write, name='zooapi.views.console.write', appname='api')),
   # закрыть консоль
   (r'/api/2/console/cancel/$', CommonRequestHandler,
    dict(callable_object=cancel, name='zooapi.views.console.cancel', appname='api')),
   # проверка коннекта в бд, используется на мастере инсталляции приложения
   (r'/api/2/db/check/', CommonRequestHandler,
    dict(callable_object=check, name='zooapi.views.db.check', appname='api')),
   # настройки
   (r'/api/2/settings/$', SettingsRequestHandler,
    dict(callable_object=settings, name='zooapi.views.settings.settings', appname='api')),
   # состояние ядра (загружается, загружено, с ошибками)
   (r'/api/2/core/state/$', CommonRequestHandler,
    dict(callable_object=state, name='zooapi.views.core.state', appname='api')),
   # проверяет, есть ли обновление для нас
   (r'/api/2/core/upgrade/$', CommonRequestHandler,
    dict(callable_object=has_upgrade, name='zooapi.views.core.has_upgrade', appname='api')),
   (r'/api/2/core/sync/$', CommonRequestHandler,
    dict(callable_object=sync, name='zooapi.views.core.sync', appname='api')),
   # размер директории кеша
   (r'/api/2/core/cache/$', CommonRequestHandler,
    dict(callable_object=cache, name='zooapi.views.core.cache', appname='api')),
   # очистить директорию кеша
   (r'/api/2/core/cache/clear/$', CommonRequestHandler,
    dict(callable_object=cache_clear, name='zooapi.views.core.cache_clear', appname='api')),
   # размер директории логов
   (r'/api/2/core/logs/$', CommonRequestHandler,
    dict(callable_object=logs, name='zooapi.views.core.logs', appname='api')),
   # очистить директорию логов
   (r'/api/2/core/logs/clear/$', CommonRequestHandler,
    dict(callable_object=logs_clear, name='zooapi.views.core.logs_clear', appname='api'))

]

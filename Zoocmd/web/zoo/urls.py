# -*- coding: utf-8 -*-


"""
По всем этим урлам отдаётся простая html-страничка,
вся логика веб-интерфейса находится в джсе.
Исключение — 'zoo.views.task_log'. Для скорости богатый цветной лог таска рендерится на сервере,
с помощью шаблона.
"""

from web.zoo.views import home, server, gallery, install, install_application
from web.zoo.views import upgrade, uninstall, task_list, task, task_log
from web.zoo.views import settings_view, console, icon, update, cancel_task
from web.helpers.http import CommonRequestHandler, IconRequestHandler
from web.helpers.http import CommonRequestHandlerOneParam, SettingsRequestHandler

application_urls = [(r'/', CommonRequestHandler,  dict(callable_object=home, name="home", appname='front')),
                    (r'/server/$', CommonRequestHandler,  dict(callable_object=server, name="server",
                                                               appname='front')),
                    (r'/gallery/$', CommonRequestHandler, dict(callable_object=gallery, name="gallery",
                                                               appname='front')),
                    (r'/install/application/$', CommonRequestHandler, dict(callable_object=install_application,
                                                                           name='install',
                                                                           appname='front')),
                    (r'/install/$', CommonRequestHandler, dict(callable_object=install, name='install',
                                                               appname='front')),
                    (r'/cancel_install/$', CommonRequestHandler, dict(callable_object=install,
                                                                      name='cancel_install',
                                                                      appname='front')),
                    (r'/upgrade/$', CommonRequestHandler, dict(callable_object=upgrade, name='upgrade',
                                                               appname='front')),
                    (r'/uninstall/$', CommonRequestHandler, dict(callable_object=uninstall, name='uninstall',
                                                                 appname='front')),
                    (r'/task/$', CommonRequestHandler, dict(callable_object=task_list, name='task_list',
                                                            appname='front')),
                    (r'/task/(?P<param1>\d+)/$', CommonRequestHandlerOneParam, dict(callable_object=task,
                                                                                    name='task_id',
                                                                                    appname='front')),

                    (r'/cancel_task/(?P<param1>\d+)/$', CommonRequestHandlerOneParam, dict(callable_object=cancel_task,
                                                                                           name='cancel_task_id',
                                                                                           appname='front')),

                    (r'/task/(?P<param1>\d+)/log/$', CommonRequestHandlerOneParam, dict(callable_object=task_log,
                                                                                        name='task_id_log',
                                                                                        appname='front')),
                    (r'/settings/$', SettingsRequestHandler, dict(callable_object=settings_view, name='settings_view',
                                                                appname='front')),
                    (r'/console/$', CommonRequestHandler, dict(callable_object=console, name='console',
                                                               appname='front')),
                    (r'/update/$', CommonRequestHandler, dict(callable_object=update, name='update',
                                                              appname='front')),
                    (r'/product/(?P<product_name>[^/]+)/icon/', IconRequestHandler, dict(callable_object=icon,
                                                                                         name='icon',
                                                                                         appname='front'
                                                                                         ))
                    ]


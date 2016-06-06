# -*- coding: utf-8 -*-

import os.path
import mimetypes
"""
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, render_to_response, get_object_or_404

from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
"""

from web.helpers.http import Http404, HttpResponse, HttpResponseRedirect, get_object_or_404
from web.helpers.template import render_to_response, request_context


from core.core import Core
from core.core_loader import CoreLoader
from core.job import Job
from core.models.database import JobPeewee as JobDataModel
import urllib.parse
import web.web_settings



def cancel_task(request, task_id):
    task_id = int(task_id)
    redirect_to=None
    redirect_to = request.GET.get("back", None)
    if redirect_to is None:
        redirect_to="/"

    try:
        if task_id !=0 :
            job = Job.get_job(task_id)
            job.job2canceled()
    except:
        # just do nothing
        pass

    return HttpResponseRedirect(redirect_to)


def select_webserver(request):
    return render_to_response(web.web_settings.template_environment, 'req_server_choose.html',
                              request_context(request))

def wait_core(request):
    return render_to_response(web.web_settings.template_environment, 'wait_core.html',
                              request_context(request))

# @ensure_csrf_cookie
def home(request):
    return render_to_response(web.web_settings.template_environment, 'home.html',
                              request_context(request))


# @ensure_csrf_cookie
def server(request):
    return render_to_response(web.web_settings.template_environment, 'server.html',
                              request_context(request))


# @ensure_csrf_cookie
def gallery(request):
    return render_to_response(web.web_settings.template_environment, 'gallery.html',
                              request_context(request))


def settings_view(request):
    return render_to_response(web.web_settings.template_environment, 'settings.html',
                              request_context(request))



def icon(request, product_name):
    """
    Возвращает иконку (бинарное содерживое файла) для продукта
    """

    # находим путь к иконке
    core = Core.get_instance()
    product = core.feed.get_product(product_name)
    icon_path = product.icon
    if not icon_path:
        raise Http404()

    # если путь урл — отсылаеи редирект
    if icon_path.startswith('http'):
        return HttpResponseRedirect(icon_path)

    if not os.path.exists(icon_path):
        # такого пути нет - 404
        raise Http404()

    # получаем миме-тип иконки
    mimetype = mimetypes.guess_type(os.path.basename(icon_path))[0]

    # читаем содержимое файла иконки
    with open(icon_path, 'rb') as fh:
        response = HttpResponse(body=fh.read())

    # ставим кеширующий хидер
    response["Content-Type"] = mimetype
    response['Cache-Control'] = 'public,max-age=3600'
    return response


# this function starts  installing application
# return master js application
def install_application(request):
    application_name = request.REQUEST.get("products")
    # context =  {"master_title": "Installing application " + application_name}
    return render_to_response(web.web_settings.template_environment, 'install_application.html',
                       request_context(request))



# this function starts  installing product
# return master js application
def install(request):
    # context =  {"master_title": "Installing product(s)"}
    return render_to_response(web.web_settings.template_environment, 'install2.html',
                       request_context(request))


def upgrade(request):
    return render_to_response(web.web_settings.template_environment, 'upgrade.html',
                              request_context(request))


def uninstall(request):
    # context = {"master_title": u"Uninstalling Product(s)"}
    return render_to_response(web.web_settings.template_environment, 'uninstall.html',
                              request_context(request))

def task_list(request):
    return render_to_response(web.web_settings.template_environment, 'task_list.html',
                              request_context(request))

def task(request, job_id):
    t = get_object_or_404(JobDataModel, id=job_id)
    return render_to_response(web.web_settings.template_environment, 'task.html',
                              request_context(request, {'task': t}))


# It is not  used any more!!
def task_log(request, job_id):
    # получаем объект таска
    t = get_object_or_404(JobDataModel, id=job_id)
    # и его логи
    logs = t.get_logs(None)
    # рендерим логи в джанго-шаблоне
    return render_to_response(web.web_settings.template_environment, 'task_log.html',
                              request_context(request, {'task': t, 'logs': logs}))


# @ensure_csrf_cookie
def console(request):
    return render_to_response(web.web_settings.template_environment, 'console.html',
                              request_context(request))


def update(request):
    """
    Запускает апгрейд ядра и редиректит на главную, где показывает процесс создания нового ядра.
    """
    core = Core.get_instance()
    core_loader = CoreLoader.get_instance()
    core_loader.restart(core.settings)
    return HttpResponseRedirect("/")

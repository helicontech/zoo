# -*- coding: utf-8 -*-


from web.helpers.http import HttpResponseNotAllowed, get_object_or_404
from web.helpers.json import json_response, json_request, json_response_raw
from core.task_manager import TaskManager
from core.job import Job
from core.models.database import JobPeewee as JobDataModel
from core.helpers.common import kill_proc_tree

# using
@json_response_raw
def task_paging(request):
    """
    Получить список заданий

    :param request:
    :return:
    """
    # task_paging/list/?sort=created&order=desc&limit=100&offset=0"
    # ?limit=10&offset=10&order=asc
    sorting = JobDataModel.id.desc()




    if 'sort' in request.GET:
        sorting_value = request.GET['sort']
        if sorting_value == 'created':
                if 'order' in request.GET and request.GET['order'] == 'asc':
                    sorting = JobDataModel.created.asc()
                else:
                    sorting = JobDataModel.created.desc()
        if sorting_value == 'title':
                if 'order' in request.GET and request.GET['order'] == 'asc':
                    sorting = JobDataModel.title.asc()
                else:
                    sorting = JobDataModel.title.desc()
        if sorting_value == 'command':
                if 'order' in request.GET and request.GET['order'] == 'asc':
                    sorting = JobDataModel.command.asc()
                else:
                    sorting = JobDataModel.command.desc()
        if sorting_value == 'status':
                if 'order' in request.GET and request.GET['order'] == 'asc':
                    sorting = JobDataModel.status.asc()
                else:
                    sorting = JobDataModel.status.desc()

    limit = int(request.GET['limit'])
    offset = int(request.GET['offset'])
    rows = None

    if 'search' in request.GET and len(request.GET['search'])>3:
        search_string = request.GET['search']
        rows = [t.to_dict() for t in JobDataModel.select().order_by(sorting).where(JobDataModel.title.contains(search_string)).offset(offset).limit(limit) ]
        count = JobDataModel.select().where(JobDataModel.title.contains(search_string)).count()
        return {"total": count, "rows": rows}

    else:
        rows = [t.to_dict() for t in JobDataModel.select().order_by(sorting).offset(offset).limit(limit) ]
        count = JobDataModel.select().count()
        return {"total": count, "rows": rows}


# using
@json_response
def task_list(request):
    """
    Получить список заданий

    :param request:
    :return:
    """
    return [t.to_dict() for t in JobDataModel.select().order_by(JobDataModel.id.desc())]

# do not using
@json_response
def task(request, task_id):
    """
    Получить конкретное задание по номеру task_id
    :param request:
    :param task_id:
    :return:
    """
    t = get_object_or_404(JobDataModel, id=task_id)
    return t.to_dict()


# cancel running job
@json_response
def cancel_task(request, job_id):
    """
    Отменить конкретное задание по номеру task_id
    :param request:
    :param task_id:
    :return:
    """
    #TODO add is task alive
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    t = get_object_or_404(JobDataModel, id=job_id)
    t.status = t.STATUS_CANCELED
    t.save()
    if t.pid:
        kill_proc_tree(t.pid)
    return {"status": True}


# do not using
@json_response
def rerun(request, job_id):
    """
    Повторно выполнить конкретное задание по номеру job_id
    :param request:
    :param job_id:
    :return:
    """
    # TODO rewrite it there is no that TaskManager
    t = get_object_or_404(JobDataModel, id=job_id)
    task_manager = TaskManager.get_instance()
    task_manager.rerun_task(t)
    return {'task': t.to_dict()}



# USING
@json_response
def log(request, job_id):
    """
    получить логи конкретного задания по номеру
    из базы данных
    если задание выполняется, то логи могут расти

    :param request:
    :param job_id:
    :return:
    """
    since = request.GET['since']
    t = get_object_or_404(JobDataModel, id=job_id)
    resp = {
        'task': t.to_dict(),
        'log_messages': [lm.to_dict() for lm in t.get_logs(since)]
    }
    return resp

# -*- coding: utf-8 -*-
#
# todo/task_management/urls.py
#

from django.urls import path, re_path

from task_management import views

urlpatterns = [
    re_path(r"project/$", views.project, name="project"),
    re_path(r"myproject/$", views.ProjectTasks, name="project-detail"),
    re_path(r"task/$", views.Newtask, name="new_task"),
    re_path(r"mytasks/$", views.Mytasks, name="task-detail"),
    re_path(
        r"assigntask/(?P<public_id>[-\w]+)/$",
        views.Assigntask,
        name="assign_task",
    ),
    path("test/", views.test, kwargs={"name": "roya"}, name="test"),
]
# re_path(
#     r"project/(?P<public_id>[-\w]+)/$",
#     views.Project_detail,
#     name="project-detail",
# re_path(
#     r"task/(?P<public_id>[-\w]+)/$", views.task_detail, name="task-detail"
# ),
# path("test/", views.test, kwargs={"name": "roya"}, name="test"),

# -*- coding: utf-8 -*-
#
# todo/task_management/urls.py
#

from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns

from task_management import views

urlpatterns = [
    re_path(r"project/$", views.project, name="project"),
    re_path(r"myproject/$", views.Project_detail, name="project-detail"),
    re_path(r"task/$", views.task_list, name="task-list"),
    re_path(r"mytask/$", views.my_tasks, name="task-detail"),
]
# re_path(
#     r"project/(?P<public_id>[-\w]+)/$",
#     views.Project_detail,
#     name="project-detail",
# re_path(
#     r"task/(?P<public_id>[-\w]+)/$", views.task_detail, name="task-detail"
# ),
# path("test/", views.test, kwargs={"name": "roya"}, name="test"),


urlpatterns = format_suffix_patterns(urlpatterns)

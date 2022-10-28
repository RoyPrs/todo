# -*- coding: utf-8 -*-
#
# todo/urls.py
#
"""
Parent URL file.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("rest_framework.urls")),
    path("task/", include("task_management.urls")),
    path("user/", include("user_management.urls")),
]

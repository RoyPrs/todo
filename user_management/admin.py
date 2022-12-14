# -*- coding: utf-8 -*-
#
# todo/user_management/admin.py
#

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from django.contrib.auth.models import Group

admin.site.unregister(Group)

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "role", "get_project", "get_tasks_list")
    exclude = ("groups", "user_permissions")

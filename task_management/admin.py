# -*- coding: utf-8 -*-
#
# todo/task_management/admin.py
#
"""
Admin.
"""
from django.contrib import admin
from task_management.models import (
    Project,
    Task,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "get_tasks", "manager", "public_id")
    actions = ["mark_finished"]

    def do_something(self, request, queryset):
        pass

    do_something.short_description = "Do something"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "project", "get_developers", "public_id")
    actions = ["mark_finished", "mark_unfinished"]

    def mark_finished(self, request, queryset):
        queryset.filter(is_finished=False).update(is_finished=True)

    mark_finished.short_description = "Mark the task as finished"

    def mark_unfinished(self, request, queryset):
        queryset.filter(is_finished=True).update(is_finished=False)

    mark_unfinished.short_description = "Mark the task as unfinished"

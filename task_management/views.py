# -*- coding: utf-8 -*-
#
# todo/task_management/views.py
#
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.http import Http404

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_condition import C, And, Or, Not

from common.view_mixins import (
    TrapDjangoValidationErrorCreateMixin,
    TrapDjangoValidationErrorUpdateMixin,
)
from common.permissions import (
    IsAdminSuperUser,
    IsUserActive,
    IsProjectManager,
    IsDeveloper,
)

from task_management import serializers, models


UserModel = get_user_model()


def get_user(request):
    user = None
    if hasattr(request, "user"):
        user = request.user
    return user


# ------------------------------Project------------------------------


class ProjectListCreate(
    TrapDjangoValidationErrorCreateMixin, generics.ListCreateAPIView
):
    """This class provides the methods to list all projects an add new projects."""

    serializer_class = serializers.ProjectSerializer
    permission_classes = (
        And(
            IsUserActive,
            IsAuthenticated,
            Or(IsAdminSuperUser, IsProjectManager),
        ),
    )
    lookup_field = "public_id"

    def get_queryset(self):
        queryset = models.Project.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        user = get_user(request)
        data = request.data
        if user:
            data["manager"] = user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


project = ProjectListCreate.as_view()


class ProjectTaskRetrieve(
    TrapDjangoValidationErrorUpdateMixin, generics.RetrieveAPIView
):
    """This class provides a method to retrieve the project in which a manager/developer participates."""

    serializer_class = serializers.ProjectSerializer
    permission_classes = (
        And(
            IsUserActive,
            IsAuthenticated,
            Or(IsAdminSuperUser, IsProjectManager, IsDeveloper),
        ),
    )
    lookup_field = "public_id"

    def get_queryset(self):
        queryset = models.Project.objects.all()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        user = get_user(request)
        project = None
        if user:
            project = user.get_project
        serializer = self.get_serializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)


ProjectTasks = ProjectTaskRetrieve.as_view()


# ------------------------------Task------------------------------


class TaskCreate(TrapDjangoValidationErrorCreateMixin, generics.CreateAPIView):
    """This class provides a method to create a new task."""

    # queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = (
        And(
            IsUserActive,
            IsAuthenticated,
            Or(IsAdminSuperUser, IsProjectManager, IsDeveloper),
        ),
    )
    lookup_field = "public_id"

    @staticmethod
    def has_permission_to_create(project, current_project, role):
        """It is allowed to add tasks with empty project field.
         Developers with no tasks or managers with no project are also allowed to create task.
        Superuser is allowed to creat task without any limitations"""
        result = False

        if role and role == UserModel.ROLE_MAP[UserModel.SUPERUSER]:
            result = True
        elif (
            (project and current_project and current_project.pk == project)
            or not project
            or not current_project
        ):
            result = True
        return result

    def create(self, request, *args, **kwargs):
        msg = _(f"Deloper/manager can only define tasks in their own project.")
        user = get_user(request)
        data = request.data
        project = data.get("project", None)
        current_project = user.get_project
        role = None
        if user:
            role = getattr(user, "role", None)

        if not self.has_permission_to_create(project, current_project, role):
            raise PermissionDenied(msg)

        if role and role == UserModel.ROLE_MAP[UserModel.DEVELOPER]:
            data["developer"] = [user.pk]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


Newtask = TaskCreate.as_view()


class TaskRetrieve(
    TrapDjangoValidationErrorUpdateMixin, generics.RetrieveAPIView
):
    """This class provides a method to returns list of tasks assigned to a developer
    and if used by a manager lists the tasks in their project."""

    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = (
        And(
            IsUserActive,
            IsAuthenticated,
            Or(IsAdminSuperUser, IsProjectManager, IsDeveloper),
        ),
    )
    lookup_field = "public_id"

    def retrieve(self, request, *args, **kwargs):
        user = get_user(request)
        tasks = None
        if user:
            tasks = user.get_tasks
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


Mytasks = TaskRetrieve.as_view()


class TaskUpdate(TrapDjangoValidationErrorUpdateMixin, generics.UpdateAPIView):
    """This class provides a method to assign a task to a developer.
    With this update, only the developers field is allowed to change in a task,
    other fiedls are discarded"""

    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = (
        And(
            IsUserActive,
            IsAuthenticated,
            Or(IsAdminSuperUser, IsProjectManager),
        ),
    )
    lookup_field = "public_id"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = {}
        data["developers"] = request.data["developers"]
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


Assigntask = TaskUpdate.as_view()


# -------------------------------Draft-------------------------------
# from user_management.models import User


@api_view(["GET", "POST"])
def test(request, *args, **kwargs):
    # to get all sections of a term
    if request.method == "GET":
        result = False
        user = get_user(request)
        role = getattr(user, "role", "role not set")

        # data = User.students.all().values()
        print("in the view")
        # print("data= ", request.data)
        return Response({"name": role})

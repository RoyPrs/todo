# -*- coding: utf-8 -*-
#
# todo/task_management/views.py
#
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.http import Http404


from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
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
        my_priject = None
        if user.role == "DEVELOPER":
            my_project = self.get_project()

        elif user.role == "MANAGER":
            try:
                my_project = models.Project.objects.get(manager=user)
            except models.Project.DoesNotExist:
                pass
        if my_project:
            serializer = self.get_serializer(my_project)
            return Response(serializer.data)
        else:
            return Response(my_priject)


Project_detail = ProjectTaskRetrieve.as_view()


# ------------------------------Task------------------------------


class TaskListCreate(
    TrapDjangoValidationErrorCreateMixin, generics.ListCreateAPIView
):
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

    # def get_queryset(self):
    # queryset = models.Task.objects.all()
    # user = get_user(self.request)
    # role = user.role
    # if role == "DEVELOPER":
    #     queryset = models.Tasks.objects.filter(developer=user)
    # elif role == "MANAGER":
    # project = models.Project.objects.filter(manager=user).value_list()
    # print(project)
    # queryset = models.Task.objects.filter(project)
    # print(queryset)
    # return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if user.role == "DEVELOPER":
            data["developer"] = [user.pk]
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


task_list = TaskListCreate.as_view()


class TaskRetrieve(
    TrapDjangoValidationErrorUpdateMixin, generics.RetrieveAPIView
):
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
        """For developers returns list of tasks assigned to them, for managers list of tasks in their project."""
        user = get_user(request)
        my_tasks = {}
        if user:
            if user.role == "DEVELOPER":
                my_tasks = user.task_set.all()
            elif user.role == "MANAGER":
                try:
                    my_tasks = models.Project.objects.get(
                        manager=user
                    ).tasks.all()
                except models.Project.DoesNotExist:
                    pass
        if my_tasks:
            serializer = self.get_serializer(my_tasks, many=True)
            return Response(serializer.data)
        else:
            result = {}
            return Response(result)


my_tasks = TaskRetrieve.as_view()
# -------------------------------Draft-------------------------------
# from user_management.models import User


@api_view(["GET", "POST"])
def test(request, *args, **kwargs):
    # to get all sections of a term
    if request.method == "GET":
        # data = User.students.all().values()
        print("in the view")
        print("data= ", request.data)
        return Response({"name": request.data})


# A third common method is save() method which lets us customize how a model is saved.
# A common example is for a blog app that needs to automatically set the author of a blog pos
# t to the current logged-in user. You'd implement that functionality with save().
# To be applied for the view in which the instructor enters the grades.
# The name of the instructor should be extracted from the request.

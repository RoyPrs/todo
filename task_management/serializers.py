# -*- coding: utf-8 -*-
#
# parnia/course_management/serializers.py
#

import datetime

from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from django.core.exceptions import ValidationError


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from common.serializer_mixin import SerializerMixin
from task_management import models


def get_user(request):
    user = None
    if hasattr(request, "user"):
        user = request.user
    return user


# ------------------------------Project------------------------------


class ProjectSerializer(SerializerMixin, serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    def get_tasks(self, obj):
        return obj.get_tasks()

    class Meta:
        model = models.Project
        fields = ["public_id", "name", "manager", "tasks"]
        read_only_fields = ("public_id", "local_id")

    def validate_manager(self, manager):
        msg = _(
            f"Manager must be MANAGER :-D you should either sigin as a manager or specify a manager"
        )
        if manager.role != "MANAGER":
            raise serializers.ValidationError(msg)
        return manager


# ------------------------------Task------------------------------
class TaskSerializer(SerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = [
            "id",
            "public_id",
            "name",
            "developers",
            "project",
            "due",
            "is_finished",
        ]
        read_only_fields = ("public_id",)

    def validate_developer(self, developer):
        msg = _(f"Developerr must be a developer :-D")
        for dev in developer:
            if dev.role != "DEVELOPER":
                raise serializers.ValidationError(msg)
        return developer

    # def create(self, validated_data):
    #     developers = validated_data.pop("developer", [])
    #     obj = super().create(validated_data)
    #     if developers:
    #         obj.assign_developer(developers)
    #     return obj

    def create(self, validated_data):
        print("in serializer create", validated_data)
        developers = validated_data.pop("developers", [])
        obj = super().create(validated_data)
        if developers:
            for developer in developers:
                developer.assign_tasks([obj])
        return obj

    def update(self, instance, validated_data):
        developers = validated_data.pop("developers", [])
        super().update(instance, validated_data)

        if developers:
            instance.process_prerequesits(developers)
        return instance

    # def to_representation(self, instance):
    # def validate(self, data):

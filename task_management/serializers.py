# -*- coding: utf-8 -*-
#
# parnia/course_management/serializers.py
#

import datetime

from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from common.serializer_mixin import SerializerMixin
from task_management import models

UserModel = get_user_model()


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

    def validate_developers(self, developers):
        msg = _(f"Developer must be a developer :-D")
        for dev in developers:
            if dev.role != "DEVELOPER":
                raise serializers.ValidationError(msg)
        return developers

    def create(self, validated_data):
        developers = validated_data.pop("developers", [])
        obj = super().create(validated_data)
        obj.add_developers(developers)
        return obj

    def update(self, instance, validated_data):
        developers = validated_data.get("developers", None)
        instance.add_developers(developers)
        instance.save()
        return instance

    # def to_representation(self, instance):
    # def validate(self, data):

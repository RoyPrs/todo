# -*- coding: utf-8 -*-
#
# parnia/user_management/serializers.py
#
"""
User Management serializers.
"""


from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from common.serializer_mixin import SerializerMixin

# from user_management.models import User

UserModel = get_user_model()


def get_user(request):
    user = None
    if hasattr(request, "user"):
        user = request.user
    return user


# -------------------------------Signup-------------------------------


class SignupSerializer(SerializerMixin, serializers.ModelSerializer):
    MESSAGE = _("You do not have permission to signup as {}.")
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name_or_username()

    def validate(self, data):
        request = self.get_request()
        is_staff = data.get("is_staff")
        is_superuser = data.get("is_superuser")
        role = self.initial_data.get("role")
        if role:
            data["role"] = role

        if request.method in ("POST"):
            if is_staff or is_superuser or role == 1:
                raise serializers.ValidationError(
                    {
                        "staff-superuser": self.MESSAGE.format(
                            "staff or superuser"
                        ),
                    }
                )
        return data

    def create(self, validated_data):
        print("validated data in serializer create", validated_data)
        username = validated_data.pop("username", "")
        password = validated_data.pop("password", "")
        email = validated_data.pop("email", "")
        obj = UserModel.objects.create_user(
            username, email=email, password=password, **validated_data
        )
        return obj

    class Meta:
        model = UserModel
        fields = (
            "public_id",
            "username",
            "password",
            "full_name",
            "send_email",
            "need_password",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
        )
        read_only_fields = (
            "public_id",
            "last_login",
            "date_joined",
        )
        extra_kwargs = {"password": {"write_only": True}}


# -------------------------------Signin-------------------------------


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, write_only=True)
    password = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        fields = (
            "username",
            "password",
        )

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        user = authenticate(username=username, password=password)

        if not user:
            msg = _("The entered username and/or password is not valid.")
            raise serializers.ValidationError({"username": msg})

        data["user"] = user
        return data

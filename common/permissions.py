# -*- coding: utf-8 -*-
#
# parnia/common/permissions.py
#
"""
Authorization permissions.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework import permissions

UserModel = get_user_model()


def get_user(request):
    user = None
    if hasattr(request, "user"):
        user = request.user
    return user


#
# User based permissions
#
class IsAdminSuperUser(permissions.BasePermission):
    """
    Allows access only to admin super users.
    """

    def has_permission(self, request, view):
        result = False
        user = get_user(request)
        if user and user.is_superuser:
            result = True
        print("IsAdminSuperuser:", result)
        return result


class IsDeveloper(permissions.BasePermission):
    """
    Allows access only to a developer with a profile.
    """

    def has_permission(self, request, view):
        result = False
        user = get_user(request)

        if (
            user
            and hasattr(user, "role")
            and user.role == UserModel.ROLE_MAP[UserModel.DEVELOPER]
        ):
            result = True
        print("IsDeveloper:", result)
        return result


class IsProjectManager(permissions.BasePermission):
    """
    Allows access only to a project manager with a profile.
    """

    def has_permission(self, request, view):
        result = False
        user = get_user(request)
        print("user===========", user.is_authenticated)
        if (
            user
            and hasattr(user, "role")
            and user.role == UserModel.ROLE_MAP[UserModel.MANAGER]
        ):
            result = True
            print("isprojectmanager:", result)
        return result


class IsUserActive(permissions.BasePermission):
    """
    The request is authenticated if user is active.
    """

    def has_permission(self, request, view):
        result = False
        user = get_user(request)

        if user and user.is_active:
            result = True
        print("IsActive:", result)
        return result
# -*- coding: utf-8 -*-
#
# todo/user_management/views.py
#
"""
User Management Views; Singup, Signin and Signout
"""

import base64
import re
import string

from django.contrib.auth import get_user_model, login, logout
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    RetrieveUpdateAPIView,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from rest_condition import C, And, Or, Not

from common.permissions import (
    IsAdminSuperUser,
    IsDeveloper,
    IsProjectManager,
    IsUserActive,
)
from common.view_mixins import (
    TrapDjangoValidationErrorCreateMixin,
    TrapDjangoValidationErrorUpdateMixin,
)

from user_management.serializers import SignupSerializer, SigninSerializer

UserModel = get_user_model()

#
# User
#


class UserMixin:
    def get_serializer_class(self):
        serializer = SignupSerializer
        return serializer

    def get_queryset(self):
        return UserModel.objects.all()


# -------------------------------Signup-------------------------------


class SignupView(
    TrapDjangoValidationErrorCreateMixin, UserMixin, CreateAPIView
):
    """
    Create user (sign up) endpoint.
    """

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    lookup_field = "public_id"


signup = SignupView.as_view()

# -------------------------------Retrieve a User-------------------------------


class UserDetail(
    TrapDjangoValidationErrorUpdateMixin, UserMixin, RetrieveUpdateAPIView
):
    permission_classes = (And(IsUserActive, IsAuthenticated),)
    lookup_field = "public_id"


user_detail = UserDetail.as_view()

# -------------------------------Signin-------------------------------


class SigninView(GenericAPIView):
    """
    Signin view. Performs a signin on a POST and provides the user's full
    name and the href to the user's endpoint. Credentials are required to
    signin.
    """

    serializer_class = SigninSerializer
    CHARS = string.ascii_letters + string.digits + "+/="
    # The regex below will ignore any additional parameters as per RFC7617.
    RE_SEARCH = re.compile(
        r"^.*(Basic +)(?P<enc_creds>[{}]+) *.*$".format(CHARS)
    )

    def post(self, request, *args, **kwargs):
        basic = request.META.get("HTTP_AUTHORIZATION")
        sre = self.RE_SEARCH.search("" if basic is None else basic)
        enc_creds = sre.group("enc_creds") if sre is not None else ""
        data = {}

        # Parse out the username and password.
        if len(enc_creds) > 0:
            creds = base64.b64decode(bytearray(enc_creds, "utf-8")).decode()
            username, delm, password = creds.partition(":")
            data["username"] = username
            data["password"] = password
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        login(request, user)
        result = {}
        result["detail"] = _("Successfully signed in")
        result["fullname"] = user.get_full_name_or_username()
        result["href"] = reverse(
            "user-detail", kwargs={"public_id": user.public_id}, request=request
        )

        return Response(result)


signin = SigninView.as_view()

# -------------------------------Signout-------------------------------


class SignoutView(APIView):
    """
    Signout view. Performs the signout on a POST. No POST data is required
    to signout.
    """

    # permission_classes = (And(IsUserActive, IsAuthenticated, IsAnyUser),)

    def post(self, request, *args, **kwargs):
        logout(request)
        status = HTTP_200_OK
        result = {"detail": _("Signout was successful.")}
        return Response(result, status=status)


signout = SignoutView.as_view()

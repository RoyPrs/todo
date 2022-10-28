# -*- coding: utf-8 -*-
#
# todo/user_management/urls.py
#
"""
User_management API URLs
"""

__docformat__ = "restructuredtext en"

from django.urls import re_path, path
from user_management import views


urlpatterns = [
    re_path(r"signup/$", views.signup, name="signup"),
    re_path(r"signin/$", views.signin, name="signin"),
    re_path(r"signout/$", views.signout, name="signout"),
    re_path(
        r"users/(?P<public_id>[-\w]+)/$", views.user_detail, name="user-detail"
    ),
]

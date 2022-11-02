# -*- coding: utf-8 -*-
#
# todo/user_management/models.py
#

"""
User model.
"""
__docformat__ = "restructuredtext en"

import logging

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail

from common import generate_public_key
from common.model_mixins import ValidateOnSaveMixin


log = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    def _create_user(
        self, username, email, password, is_staff, is_superuser, **extra_fields
    ):
        """
        Creates and saves a User with the given username, email and password.
        """

        if not username:
            raise ValueError(_("The username must be set."))

        email = self.normalize_email(email)
        role = extra_fields.pop("role", self.model.DEVELOPER)

        if not password:
            if email:
                password = self.make_random_password()
                extra_fields["send_email"] = True
                extra_fields["need_password"] = True
            else:
                raise ValueError(
                    _("User must have a valid email or a password.")
                )
        else:
            extra_fields["send_email"] = False
            extra_fields["need_password"] = False

        now = timezone.now()
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user._role = role
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(
            username, email, password, False, False, **extra_fields
        )

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(
            username, email, password, True, True, **extra_fields
        )


class DeveloperManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(_role=self.model.DEVELOPER)


class ManagerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(_role=self.model.MANAGER)


class User(AbstractUser, ValidateOnSaveMixin, models.Model):

    SUPERUSER = 1
    MANAGER = 2
    DEVELOPER = 3

    ROLE = (
        (SUPERUSER, _("SUPERUSER")),
        (MANAGER, _("MANAGER")),
        (DEVELOPER, _("DEVELOPER")),
    )
    ROLE_MAP = {k: v for k, v in ROLE}
    ROLE_MAP_REV = {v: k for k, v in ROLE}

    YES = True
    NO = False
    YES_NO = (
        (YES, _("Yes")),
        (NO, _("No")),
    )

    MALE = "Male"
    FEMALE = "Female"
    NOT_SELECTED = "Not selected"
    GENDERS = (
        (MALE, _("Male")),
        (FEMALE, _("Female")),
        (NOT_SELECTED, _("Not selected")),
    )
    username_validator = UnicodeUsernameValidator()

    public_id = models.CharField(
        verbose_name=_("Public User ID"),
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
        help_text=_("Public ID unique to each user."),
    )
    _role = models.SmallIntegerField(
        verbose_name=_("Role"),
        choices=ROLE,
        default=DEVELOPER,
        help_text=_("The role of the user."),
    )

    send_email = models.BooleanField(
        verbose_name=_("Send Email"),
        choices=YES_NO,
        default=NO,
        help_text=_("Set to YES if this user needs to be sent an email."),
    )
    need_password = models.BooleanField(
        verbose_name=_("Need Password"),
        choices=YES_NO,
        default=NO,
        help_text=_("Set to YES if this user needs to reset their password."),
    )
    gender = models.CharField(
        verbose_name="Gender",
        max_length=20,
        choices=GENDERS,
        default=NOT_SELECTED,
    )

    objects = UserManager()
    developers = DeveloperManager()
    project_managers = ManagerManager()

    def clean(self):
        # Populate the public_id on record creation only.
        if self.pk is None and not self.public_id:
            self.public_id = generate_public_key()
            if self.is_superuser:
                self._role = self.SUPERUSER

        if self._role not in self.ROLE_MAP:
            msg = _(
                f"Invalid user role, must be one of "
                f"{list(self.ROLE_MAP_REV.keys())}."
            )
            log.error(msg)
            raise ValidationError({"role": msg})

    # log.info("Public ID created %s", self.public_id)

    class Meta:
        ordering = (
            "last_name",
            "username",
        )
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.get_full_name_reversed()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("user-detail", args=[self.public_id])

    def get_full_name_or_username(self):
        result = self.get_full_name()
        if result.strip() == "":
            result = self.username
        return result

    def get_full_name_reversed(self):
        result = ""
        if self.last_name or self.first_name:
            result = "{}, {}".format(self.last_name, self.first_name)
        else:
            result = self.username
        return result

    @property
    def role(self):
        return self.ROLE_MAP[self._role]

    @property
    def get_project(self):
        """This method retrieves the project assigned to a manager/developer"""

        role = None
        project = None
        if hasattr(self, "role"):
            role = self.role
        if role:
            if role == self.ROLE_MAP[self.MANAGER]:
                from django.apps import apps

                Project = apps.get_model("task_management", "Project")
                try:
                    project = Project.objects.get(manager=self)
                except Project.DoesNotExist:
                    return project
            elif role == self.ROLE_MAP[self.DEVELOPER]:
                try:
                    project = self.task_set.first().project
                except AttributeError:
                    return project
        return project

    def assign_project(self, project):
        """
        This method assigns project to a project manager.

        """
        msg = _(f"Projects can be only assigned to project managers.")
        role = getattr(self, "role", None)
        if role and role != self.ROLE_MAP[self.MANAGER]:
            raise ValidationError({"role": msg})
        self.project = project
        self.save()

    @property
    def get_tasks(self):
        """This method retrieves the tasks if the user is a developer.
        For managers returns list of tasks in their project."""
        role = None
        tasks = None
        if hasattr(self, "role"):
            role = self.role
        if role:
            if role == self.ROLE_MAP[self.MANAGER]:
                from django.apps import apps

                Project = apps.get_model("task_management", "Project")
                try:
                    project = Project.objects.get(manager=self)
                    tasks = project.tasks.all()
                except Project.DoesNotExist:
                    return tasks
            elif role == self.ROLE_MAP[self.DEVELOPER]:
                try:
                    tasks = self.task_set.all()
                except AttributeError:
                    return tasks
        return tasks

    def get_tasks_list(self):
        tasks = self.get_tasks
        result = []
        if tasks:
            result = list(tasks)
        return result

    def assign_tasks(self, tasks):
        """
        This method assigns tasks to a developer.

        """
        msg1 = _(f"Tasks can be only assigned to developers.")
        msg2 = _(f"Every developer can participate only in one project.")
        role = None
        if self.role:
            role = self.role
        if role:
            if role != self.ROLE_MAP[self.DEVELOPER]:
                raise ValidationError({"role": msg1})
        new_projects = [task.project for task in tasks if task.project]
        if len(set(new_projects)) > 1:
            raise ValidationError({"project": msg2})

        current_project = self.get_project
        if current_project:
            all_projects = new_projects + [current_project]
        else:
            all_projects = new_projects

        if len(set(all_projects)) > 1:
            raise ValidationError({"project": msg2})
        self.task_set.add(*tasks)

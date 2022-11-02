# -*- coding: utf-8 -*-
#
# todo/task_management/models.py
#
import logging
import datetime

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from common.model_mixins import ValidateOnSaveMixin
from common import generate_public_key

log = logging.getLogger("todo.user_management.models")
UserModel = get_user_model()


# ------------------------------Project------------------------------
class Project(ValidateOnSaveMixin, models.Model):

    public_id = models.CharField(
        verbose_name=_("Public Project ID"),
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
        help_text=_("Public ID unique to each project"),
    )

    name = models.CharField(
        verbose_name=_("Project Name"),
        max_length=50,
        unique=False,
        help_text=_("Name of the project"),
    )
    manager = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name=_("Project Manager"),
        help_text=_("Project Manager"),
        blank=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Project"
        verbose_name_plural = "Projectss"

    def clean(self):
        # Populate the public_id on record creation only.
        if self.pk is None and not self.public_id:
            self.public_id = generate_public_key()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("project-detail", kwargs={"pulic_id": self.pulic_id})

    def get_tasks(self):
        tasks = list(self.tasks.values_list("name", flat=True))
        return tasks or "No tasks set yet."

    def assign_project_manager(self, manager):
        manager.assign_project(self)

    def discharge_project_manager(self, manager):
        pass

    def add_tasks(self, tasks):
        pass

    def remove_tasks(self, tasks):
        pass

    @property
    def is_finished(self):
        result = False
        tasks = self.get_tasks()
        result = any([task.is_finished for task in tasks])
        return result


# ------------------------------Task------------------------------
class Task(ValidateOnSaveMixin, models.Model):

    public_id = models.CharField(
        verbose_name=_("Public Task ID"),
        max_length=30,
        unique=True,
        blank=True,
        editable=False,
        help_text=_("Public ID unique to each task"),
    )

    name = models.CharField(
        verbose_name=_("Task Name"),
        max_length=50,
        unique=False,
        help_text=_("Name of the task"),
    )

    developers = models.ManyToManyField(
        UserModel,
        verbose_name=_("Developer"),
        help_text=_("The developer who is sopposed to do the task"),
        symmetrical=False,
        blank=True,
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("Corresponding Project"),
        help_text=_("The project in which this task is defined"),
        related_name="tasks",
    )

    due = models.DateField(
        verbose_name=_("Due Date"),
        blank=True,
        help_text=_("The date on which the task is due to finish"),
    )

    is_finished = models.BooleanField(
        verbose_name=_("Is finished"),
        blank=True,
        help_text=_("Is the task finished or not"),
        default=True,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def clean(self):
        # Populate the public_id on record creation only.
        if self.pk is None and not self.public_id:
            self.public_id = generate_public_key()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("task-detail", kwargs={"public_id": self.public_id})

    @property
    def isDue(self):
        """Checks if the task is due or not"""

        today = datetime.date.today()
        return self.due < today

    def add_developers(self, developers):
        """
        Assigns the task to developers.

        """
        for developer in developers:
            developer.assign_tasks((self,))

    def discharge_developer(self, developers):
        """Removes a developer from a task"""
        pass

    @property
    def get_developers(self):
        """Returns list of developers assigned to a task"""

        developers = list(self.developers.values_list("username", flat=True))
        return developers or "No developers assigned yet."


# ------------------------------Draft------------------------------

# choices
# database fields
# custom manager attributes
# Meta
# def __str__()
# def save()
# def get_absolute_url()
# custom methods

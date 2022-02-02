from collections import Sequence
from typing import Final

from django.db import models
from django.utils.translation import gettext_lazy as _


class RelatedToProject(models.Model):
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("project"),
    )

    class Meta:
        abstract = True


class RelatedToIssue(models.Model):
    issue = models.ForeignKey(
        "project.Issue",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("issue"),
    )

    class Meta:
        abstract = True


DEVELOPER = "developer"
MAINTAINER = "maintainer"
ROLES: Final[Sequence[tuple[str, str]]] = (
    (DEVELOPER, _("Developer")),
    (MAINTAINER, _("Maintainer")),
)


PENDING = "pending"
ACCEPTED = "accepted"
REJECTED = "rejected"
INVITATION_STATUSES: Final[Sequence[tuple[str, str]]] = (
    (PENDING, _("Pending")),
    (ACCEPTED, _("Accepted")),
    (REJECTED, _("Rejected")),
)


NEW = "new"
IN_PROGRESS = "in-progress"
CLOSED = "closed"
RELEASE_READY = "release-ready"
TASK_STATUSES: Final[Sequence[tuple[str, str]]] = (
    (NEW, _("New")),
    (IN_PROGRESS, _("In progress")),
    (CLOSED, _("Closed")),
    (RELEASE_READY, _("Release ready")),
)

TASK = "task"
USER_STORY = "user-story"
BUG = "bug"
TASK_TYPES: Final[Sequence[tuple[str, str]]] = (
    (TASK, _("Task")),
    (USER_STORY, _("User story")),
    (BUG, _("Bug")),
)

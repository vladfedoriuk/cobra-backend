from typing import Sequence, Union

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from cobra.project.managers import ProjectManager
from cobra.project.utils.models import ProjectRelated
from cobra.utils.models import (
    TimeStampedAndCreatedByUser,
    TimeStampedAndRelatedToUser,
    TimeStampedModel,
    UUIDPrimaryKeyModel,
)


class Project(TimeStampedAndCreatedByUser):
    title = models.CharField(_("title"), max_length=250)
    slug = models.SlugField(_("slug"), max_length=250)

    class Meta:
        constraints: list[
            Union[models.UniqueConstraint, models.Deferrable, models.CheckConstraint]
        ] = [
            models.UniqueConstraint(
                fields=["slug", "creator"], name="slug_and_creator_unique_constraint"
            )
        ]

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="project.ProjectMembership",
        through_fields=("project", "user"),
        related_name="projects",
        related_query_name="project",
    )

    objects: models.Manager["Project"] = ProjectManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.title))
        return super().save(*args, **kwargs)

    def __repr__(self):
        return f"Project(creator='{self.creator.username}', slug='{self.slug}')"

    def __str__(self):
        return f"{self.creator.username}:{self.slug}"


DEVELOPER = "developer"
MAINTAINER = "maintainer"
ROLES: Sequence[tuple[str, str]] = (
    (DEVELOPER, _("Developer")),
    (MAINTAINER, _("Maintainer")),
)


class ProjectMembership(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("project"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    role = models.CharField(_("role"), max_length=20, choices=ROLES, default=DEVELOPER)

    class Meta:
        constraints: list[
            Union[models.UniqueConstraint, models.Deferrable, models.CheckConstraint]
        ] = [
            models.UniqueConstraint(
                fields=["project", "user"], name="project_and_user_unique_constraint"
            )
        ]


PENDING = "pending"
ACCEPTED = "accepted"
REJECTED = "rejected"
INVITATION_STATUSES: Sequence[tuple[str, str]] = (
    (PENDING, _("Pending")),
    (ACCEPTED, _("Accepted")),
    (REJECTED, _("Rejected")),
)


class ProjectInvitation(
    TimeStampedAndRelatedToUser, ProjectRelated, UUIDPrimaryKeyModel
):
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("inviter"),
        related_name="created_invitations",
    )
    status = models.CharField(
        _("status"), max_length=20, choices=INVITATION_STATUSES, default=PENDING
    )

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.created + settings.PROJECT_INVITATION_LIFETIME

    def get_absolute_url(self) -> str:
        return settings.PROJECT_INVITATION_URL.format(id=self.id)

    def send(self):
        from cobra.project.tasks import send_project_invitation_email

        if self.pk is not None:
            send_project_invitation_email.apply_async(kwargs={"invitation_pk": self.pk})

    def __repr__(self):
        return f"ProjectInvitation(inviter={self.inviter}, invited={self.user}, project={self.project}"

    def __str__(self):
        return f"{self.inviter} invites {self.user} to join a project {self.project}"


class Epic(TimeStampedAndCreatedByUser, ProjectRelated):
    title = models.CharField(_("title"), max_length=250)
    description = models.TextField(_("description"))


NEW = "new"
IN_PROGRESS = "in-progress"
CLOSED = "closed"
RELEASE_READY = "release-ready"
TASK_STATUSES: Sequence[tuple[str, str]] = (
    (NEW, _("New")),
    (IN_PROGRESS, _("In progress")),
    (CLOSED, _("Closed")),
    (RELEASE_READY, _("Release ready")),
)


class Task(TimeStampedAndCreatedByUser, ProjectRelated):
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("assignee"),
        related_name="assigned_tasks",
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("status"), max_length=20, choices=TASK_STATUSES, default=NEW
    )
    title = models.CharField(_("title"), max_length=250)
    description = models.TextField(_("description"))
    estimate = models.DecimalField(
        _("time estimate"),
        help_text=_("Time estimation in hours."),
        decimal_places=2,
        max_digits=5,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        verbose_name=_("parent task"),
        related_name="subtasks",
        blank=True,
        null=True,
    )
    epic = models.ForeignKey(
        Epic,
        on_delete=models.CASCADE,
        verbose_name=_("related epic"),
        related_name="tasks",
    )

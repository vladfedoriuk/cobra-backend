from typing import Sequence, Union

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from cobra.project.managers import ProjectManager
from cobra.utils.models import TimeStampedAndOwnedByUser, TimeStampedModel


class Project(TimeStampedAndOwnedByUser):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)

    class Meta:
        constraints: list[
            Union[models.UniqueConstraint, models.Deferrable, models.CheckConstraint]
        ] = [
            models.UniqueConstraint(
                fields=["slug", "user"], name="slug_and_user_unique_constraint"
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
        return f"Project(user='{self.user.username}', slug='{self.slug}')"

    def __str__(self):
        return f"{self.user.username}:{self.slug}"


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

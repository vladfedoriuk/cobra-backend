from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectRelated(models.Model):
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("project"),
    )

    class Meta:
        abstract = True

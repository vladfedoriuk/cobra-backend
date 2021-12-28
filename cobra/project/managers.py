from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

from cobra.project.querysets import ProjectQueryset

ModelType = TypeVar("ModelType", bound=models.Model)


class ProjectManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return ProjectQueryset[ModelType](self.model, using=self._db)

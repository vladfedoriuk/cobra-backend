from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

from cobra.project.querysets import ProjectQueryset
from cobra.project.utils.models import BUG, TASK, USER_STORY

ModelType = TypeVar("ModelType", bound=models.Model)


class ProjectManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return ProjectQueryset[ModelType](self.model, using=self._db)


class TaskManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return super().get_queryset().filter(type=TASK)


class BugManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return super().get_queryset().filter(type=BUG)


class UserStoryManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return super().get_queryset().filter(type=USER_STORY)

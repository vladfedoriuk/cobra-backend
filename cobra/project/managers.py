from functools import partialmethod
from typing import TYPE_CHECKING, Optional, TypeVar

from django.db import models
from django.db.models import QuerySet

from cobra.project.querysets import (
    EpicQueryset,
    IssueQueryset,
    ProjectMembershipQueryset,
    ProjectQueryset,
)
from cobra.project.utils.models import BUG, DEVELOPER, MAINTAINER, TASK, USER_STORY
from cobra.user.models import CustomUser

if TYPE_CHECKING:
    from cobra.project.models import Project
else:
    Project = "Project"

ModelType = TypeVar("ModelType", bound=models.Model)


class ProjectManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return ProjectQueryset[ModelType](self.model, using=self._db)


class ProjectMembershipManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return ProjectMembershipQueryset[ModelType](self.model, using=self._db)

    def is_user_project_member(
        self, user: CustomUser, project: Project, role: Optional[str] = None
    ) -> bool:
        qs = self.get_queryset().filter(user=user, project=project)
        if role is not None:
            qs = qs.filter(role=role)
        return qs.exists()

    is_user_project_developer = partialmethod(is_user_project_member, role=DEVELOPER)

    is_user_project_maintainer = partialmethod(is_user_project_member, role=MAINTAINER)

    def is_user_project_member_or_creator(
        self, user: CustomUser, project: Project, role: Optional[str] = None
    ):
        return (
            self.is_user_project_member(user, project, role) or project.creator == user
        )

    is_user_project_developer_or_creator = partialmethod(
        is_user_project_member_or_creator, role=DEVELOPER
    )

    is_user_project_maintainer_or_creator = partialmethod(
        is_user_project_member_or_creator, role=MAINTAINER
    )


class IssueManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return IssueQueryset[ModelType](self.model, using=self.db)

    def filter_for_project(self, project: Project) -> QuerySet[ModelType]:
        return self.filter(project=project)


class EpicManager(models.Manager[ModelType]):
    use_in_migrations = True

    def get_queryset(self) -> QuerySet[ModelType]:
        return EpicQueryset[ModelType](self.model, using=self.db)

    def filter_for_project(self, project: Project) -> QuerySet[ModelType]:
        return self.filter(project=project)


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

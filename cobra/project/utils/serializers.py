from functools import cached_property
from typing import Optional, Union, cast

from django.contrib.auth.models import AnonymousUser
from rest_framework.request import Request
from rest_framework.serializers import Serializer

from cobra.project.models import Issue, Project
from cobra.user.models import CustomUser


class BaseSerializerMixin:
    @cached_property
    def context_user(self) -> Optional[Union[CustomUser, AnonymousUser]]:
        request: Optional[Request] = cast(Serializer, self).context.get("request", None)
        if request is not None:
            return request.user
        return None


class ProjectSerializersMixin(BaseSerializerMixin):
    @cached_property
    def context_project(self) -> Optional[Project]:
        project: Optional[Project] = cast(Serializer, self).context.get("project", None)
        return project


class IssueSerializerMixin(BaseSerializerMixin):
    @cached_property
    def context_issue(self) -> Optional[Project]:
        issue: Optional[Issue] = cast(Serializer, self).context.get("issue", None)
        return issue


COMMON_USER_FIELDS: list[str] = ["id", "username", "full_name"]
COMMON_ISSUE_FIELDS: list[str] = ["id", "username", "full_name"]
COMMON_PROJECT_FIELDS: list[str] = ["id", "title", "type", "status", "assignee"]

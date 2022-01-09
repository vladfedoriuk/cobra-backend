from typing import Any, Optional

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.project.api.serializers.epic import EpicSerializer
from cobra.project.api.serializers.project import (
    ProjectSerializer,
    ReadOnlyCreatedModifiedMeta,
)
from cobra.project.models import Bug, Epic, Issue, Project, Task, UserStory
from cobra.project.utils.models import BUG, TASK
from cobra.project.utils.serializers import (
    COMMON_PROJECT_FIELDS,
    COMMON_USER_FIELDS,
    ProjectSerializersMixin,
)
from cobra.user.models import CustomUser
from cobra.user.utils.serializers import CustomUserSerializer
from cobra.utils.serializers import CustomValidationErrorsMixin


class IssueSerializer(
    FlexFieldsModelSerializer, ProjectSerializersMixin, CustomValidationErrorsMixin
):
    default_error_messages = {
        "creator_is_not_a_member_or_project_creator": _(
            "The issue creator is not a member of the project the issue belongs to."
        ),
        "assignee_is_not_project_member": _(
            "The assignee must be a member of the project the issue belongs to."
        ),
        "epic_has_wrong_project": _(
            "The epic must belong to the same project as the issue."
        ),
        "parent_has_wrong_project": _(
            "The parent issue must belong to the same project as the issue."
        ),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_queryset = Project.objects.all()
        if project_pk := getattr(self.context_project, "pk", None):
            project_queryset = project_queryset.filter(pk=project_pk)
        self.project_pk = project_pk

        self.fields["project"] = serializers.PrimaryKeyRelatedField(
            queryset=project_queryset
        )

        creator_queryset = CustomUser.objects.filter(is_active=True)
        if creator_pk := getattr(self.context_user, "pk", None):
            creator_queryset = creator_queryset.filter(pk=creator_pk)
        self.user_pk = creator_pk

        self.fields["creator"] = serializers.PrimaryKeyRelatedField(
            queryset=creator_queryset
        )

        assignee_queryset = CustomUser.objects.filter(is_active=True)
        if creator_pk and project_pk:
            assignee_queryset = assignee_queryset.filter(
                Q(pk=creator_pk) | Q(project__pk__in=[project_pk])
            ).distinct()

        self.fields["assignee"] = serializers.PrimaryKeyRelatedField(
            queryset=assignee_queryset, required=False
        )

        parent_queryset = Issue.objects.all()
        if project_pk:
            parent_queryset = parent_queryset.filter(project__pk=project_pk)

        self.fields["parent"] = serializers.PrimaryKeyRelatedField(
            queryset=parent_queryset, required=False
        )

        epic_queryset = Epic.objects.all()
        if project_pk:
            epic_queryset = epic_queryset.filter(project__pk=project_pk)

        self.fields["epic"] = serializers.PrimaryKeyRelatedField(
            queryset=epic_queryset, required=False
        )

    class Meta(ReadOnlyCreatedModifiedMeta):
        model = Issue
        fields = "__all__"
        expandable_fields = {
            "creator": (CustomUserSerializer, {"fields": COMMON_USER_FIELDS}),
            "assignee": (CustomUserSerializer, {"fields": COMMON_USER_FIELDS}),
            "project": (ProjectSerializer, {"fields": COMMON_PROJECT_FIELDS}),
            "epic": EpicSerializer,
            "parent": "cobra.project.api.serializers.issue.IssueSerializer",
        }

    def run_validation(self, data: dict[str, Any]):
        if self.instance is None:
            data.setdefault("creator", self.creator_pk)
            data.setdefault("project", self.project_pk)
        validated_data = super().run_validation(data)
        creator: Optional[CustomUser] = validated_data.get("creator")
        project: Optional[Project] = validated_data.get("project")
        assignee: Optional[CustomUser] = validated_data.get("assignee")
        epic: Optional[Epic] = validated_data.get("epic")
        parent: Optional[Issue] = validated_data.get("parent")
        if (
            project
            and creator
            and creator not in project.members.all()
            and creator != project.creator
        ):
            self.fail_with_default_error("creator_is_not_a_member_or_project_creator")
        if (
            project
            and assignee
            and not (project.members.all().filter(pk=assignee.pk).exists())
        ):
            self.fail_with_default_error("assignee_is_not_project_member")
        if project and epic and epic.project != project:
            self.fail_with_default_error("epic_has_wrong_project")
        if parent and parent.project != project:
            self.fail_with_default_error("parent_has_wrong_project")
        return validated_data


class TaskSerializer(IssueSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].choices = (TASK,)

    class Meta(IssueSerializer.Meta):
        model = Task


class BugSerializer(IssueSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].choices = (BUG,)

    class Meta(IssueSerializer.Meta):
        model = Bug


class UserStorySerializer(IssueSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].choices = (UserStory,)

    class Meta(IssueSerializer.Meta):
        model = UserStory

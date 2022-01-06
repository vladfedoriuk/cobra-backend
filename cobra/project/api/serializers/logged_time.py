from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.project.api.serializers.issue import IssueSerializer
from cobra.project.api.serializers.project import ReadOnlyCreatedModifiedMeta
from cobra.project.models import Issue, LoggedTime, ProjectMembership
from cobra.project.utils.serializers import (
    COMMON_ISSUE_FIELDS,
    COMMON_USER_FIELDS,
    IssueSerializerMixin,
)
from cobra.user.models import CustomUser
from cobra.user.utils.serializers import CustomUserSerializer


class LoggedTimeSerializer(FlexFieldsModelSerializer, IssueSerializerMixin):
    default_error_messages = {
        "user_is_not_a_member_of_issue_project": _(
            "The user is not a member of the project the issue belongs to."
        )
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        issue_queryset = Issue.objects.all()
        if issue_pk := getattr(self.context_issue, "pk", None):
            issue_queryset = issue_queryset.filter(pk=issue_pk)
        self.issue_pk = issue_pk

        user_queryset = CustomUser.objects.filter(is_active=True)
        if user_pk := getattr(self.context_user, "pk", None):
            user_queryset = user_queryset.filter(pk=user_pk)
        self.user_pk = user_pk

        self.fields["issue"] = serializers.PrimaryKeyRelatedField(
            queryset=issue_queryset
        )
        self.fields["user"] = serializers.PrimaryKeyRelatedField(queryset=user_queryset)

    class Meta(ReadOnlyCreatedModifiedMeta):
        model = LoggedTime
        fields = "__all__"
        expandable_fields = {
            "user": (CustomUserSerializer, {"fields": COMMON_USER_FIELDS}),
            "issue": (
                IssueSerializer,
                {"fields": COMMON_ISSUE_FIELDS, "expand": ["assignee"]},
            ),
        }

    def run_validation(self, data: dict[str, Any]):
        if not self.instance:
            data.setdefault("user", self.user_pk)
            data.setdefault("issue", self.issue_pk)
        validated_data = super().run_validation(data)
        user: Optional[CustomUser] = validated_data.get("creator")
        issue: Optional[Issue] = validated_data.get("issue")
        if (
            issue
            and user
            and not ProjectMembership.objects.filter(
                user__pk=user.pk, project__pk=issue.project.pk
            ).exists()
        ):
            self.fail("user_is_not_a_member_of_issue_project")
        return validated_data

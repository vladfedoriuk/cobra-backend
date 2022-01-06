from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.project.api.serializers.project import (
    ProjectSerializer,
    ReadOnlyCreatedModifiedMeta,
)
from cobra.project.models import Epic, Project
from cobra.project.utils.serializers import (
    COMMON_PROJECT_FIELDS,
    COMMON_USER_FIELDS,
    ProjectSerializersMixin,
)
from cobra.user.models import CustomUser
from cobra.user.utils.serializers import CustomUserSerializer


class EpicSerializer(FlexFieldsModelSerializer, ProjectSerializersMixin):
    default_error_messages = {
        "creator_is_not_a_member_or_project_creator": _(
            "The epic creator is not a member of the project the epic belongs to."
        )
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_queryset = Project.objects.all()
        if project_pk := getattr(self.context_project, "pk", None):
            project_queryset = project_queryset.filter(pk=project_pk)
        self.project_pk = project_pk

        creator_queryset = CustomUser.objects.filter(is_active=True)
        if creator_pk := getattr(self.context_user, "pk", None):
            creator_queryset = creator_queryset.filter(pk=creator_pk)
        self.creator_pk = creator_pk

        self.fields["project"] = serializers.PrimaryKeyRelatedField(
            queryset=project_queryset
        )
        self.fields["creator"] = serializers.PrimaryKeyRelatedField(
            queryset=creator_queryset
        )

    class Meta(ReadOnlyCreatedModifiedMeta):
        model = Epic
        fields = "__all__"
        expandable_fields = {
            "creator": (CustomUserSerializer, {"fields": COMMON_USER_FIELDS}),
            "project": (ProjectSerializer, {"fields": COMMON_PROJECT_FIELDS}),
        }

    def run_validation(self, data: dict[str, Any]):
        if not self.instance:
            data.setdefault("creator", self.creator_pk)
            data.setdefault("project", self.project_pk)
        validated_data = super().run_validation(data)
        creator: Optional[CustomUser] = validated_data.get("creator")
        project: Optional[Project] = validated_data.get("project")
        if (
            project
            and creator
            and creator not in project.members.all()
            and creator != project.creator
        ):
            self.fail("creator_is_not_a_member_or_project_creator")
        return validated_data

from typing import Any, Optional

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.project.models import Project, ProjectMembership
from cobra.project.utils.serializers import COMMON_USER_FIELDS, ProjectSerializersMixin
from cobra.user.utils.serializers import CustomUserSerializer
from cobra.utils.models import get_object_or_none


class ReadOnlyCreatedModifiedMeta:
    read_only_fields = ["created", "modified"]


class ProjectSerializer(FlexFieldsModelSerializer, ProjectSerializersMixin):
    default_error_messages = {
        "user_is_not_authenticated": _(
            "User authentication is required to perform this action."
        )
    }

    class Meta(ReadOnlyCreatedModifiedMeta):
        read_only_fields = ReadOnlyCreatedModifiedMeta.read_only_fields + [
            "members",
            "creator",
        ]
        model = Project
        fields = "__all__"
        expandable_fields = {
            "members": (
                CustomUserSerializer,
                {"many": True, "fields": COMMON_USER_FIELDS},
            ),
            "creator": (
                CustomUserSerializer,
                {"many": False, "fields": COMMON_USER_FIELDS},
            ),
        }

    is_creator = serializers.SerializerMethodField()
    membership_role = serializers.SerializerMethodField()

    def create(self, validated_data: dict[str, Any]):
        user: Optional[AbstractUser] = self.context_user
        if not user or not user.is_authenticated:
            self.fail("user_is_not_authenticated")
        validated_data["creator"] = user
        return super().create(validated_data)

    def get_is_creator(self, obj: Project) -> bool:
        return bool(obj.creator == self.context_user)

    def get_membership_role(self, obj: Project) -> str:
        context_user_membership = get_object_or_none(
            ProjectMembership, user__pk=self.context_user.pk, project__pk=obj.pk
        )
        return (
            context_user_membership.role if context_user_membership is not None else ""
        )

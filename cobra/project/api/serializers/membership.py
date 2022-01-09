from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.project.api.serializers.project import (
    ProjectSerializer,
    ReadOnlyCreatedModifiedMeta,
)
from cobra.project.models import ProjectMembership
from cobra.project.utils.serializers import COMMON_PROJECT_FIELDS, COMMON_USER_FIELDS
from cobra.user.utils.serializers import CustomUserSerializer


class ProjectMembershipSerializer(FlexFieldsModelSerializer):
    class Meta(ReadOnlyCreatedModifiedMeta):
        read_only_fields = ReadOnlyCreatedModifiedMeta.read_only_fields = [
            "project",
            "user",
        ]
        model = ProjectMembership
        fields = "__all__"
        expandable_fields = {
            "user": (
                CustomUserSerializer,
                {"fields": COMMON_USER_FIELDS, "many": False},
            ),
            "project": (ProjectSerializer, {"fields": COMMON_PROJECT_FIELDS}),
        }


class ProjectMembershipPatchSerializer(serializers.ModelSerializer):
    class Meta(ReadOnlyCreatedModifiedMeta):
        model = ProjectMembership
        fields = ("role",)

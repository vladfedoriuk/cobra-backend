from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.project.api.serializers.project import (
    ProjectSerializer,
    ReadOnlyCreatedModifiedMeta,
)
from cobra.project.models import Project, ProjectInvitation, ProjectMembership
from cobra.project.utils.models import MAINTAINER, PENDING
from cobra.project.utils.serializers import (
    COMMON_PROJECT_FIELDS,
    COMMON_USER_FIELDS,
    ProjectSerializersMixin,
)
from cobra.user.models import CustomUser
from cobra.user.utils.serializers import CustomUserSerializer
from cobra.utils.serializers import CustomValidationErrorsMixin


class ProjectInvitationSerializer(
    FlexFieldsModelSerializer, ProjectSerializersMixin, CustomValidationErrorsMixin
):
    default_error_messages = {
        "inviter_is_not_a_maintainer_or_a_creator": _(
            "The inviter must be a maintainer or the creator of the project to be able to invite new users."
        ),
        "user_is_already_a_member": _("The user is already a member of the project."),
        "pending_invitation_already_exists": _(
            "There is already a pending invitation for the user to join the project."
        ),
    }

    is_active = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inviter_pk = getattr(self.context_user, "pk", None)
        self.project_pk = getattr(self.context_project, "pk", None)

    class Meta(ReadOnlyCreatedModifiedMeta):
        read_only_fields = ReadOnlyCreatedModifiedMeta.read_only_fields + ["id"]
        model = ProjectInvitation
        fields = "__all__"
        expandable_fields = {
            "project": (ProjectSerializer, {"fields": COMMON_PROJECT_FIELDS}),
            "inviter": (CustomUserSerializer, {"fields": COMMON_USER_FIELDS}),
            "user": (CustomUserSerializer, {"fields": COMMON_USER_FIELDS}),
        }

    def run_validation(self, data: dict[str, Any]):
        if not self.instance:
            data.setdefault("inviter", self.inviter_pk)
            data.setdefault("project", self.project_pk)
        validated_data = super().run_validation(data)
        inviter: Optional[CustomUser] = validated_data.get("inviter")
        project: Optional[Project] = validated_data.get("project")
        user: Optional[CustomUser] = validated_data.get("user")
        if (
            project
            and inviter
            and not (
                ProjectMembership.objects.filter(
                    user__pk=inviter.pk, role=MAINTAINER, project__pk=project.pk
                ).exists()
                or project.creator == inviter
            )
        ):
            self.fail_with_default_error("inviter_is_not_a_maintainer_or_a_creator")
        if (
            project
            and user
            and ProjectMembership.objects.filter(
                user__pk=user.pk, project__pk=project.pk
            ).exists()
        ):
            self.fail_with_default_error("user_is_already_a_member")
        if (
            project
            and user
            and inviter
            and ProjectInvitation.objects.filter(
                user__pk=user.pk,
                project__pk=project.pk,
                inviter__pk=inviter.pk,
                status=PENDING,
            ).exists()
        ):
            self.fail_with_default_error("pending_invitation_already_exists")
        return validated_data

    def get_is_active(self, obj: ProjectInvitation):
        return not obj.is_expired

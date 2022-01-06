from typing import Any, Optional

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from rest_flex_fields import FlexFieldsModelSerializer

from cobra.project.models import Project
from cobra.project.utils.serializers import COMMON_USER_FIELDS, ProjectSerializersMixin
from cobra.user.utils.serializers import CustomUserSerializer


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

    def run_validation(self, data: dict[str, Any]):
        if self.instance:
            user: Optional[AbstractUser] = self.context_user
            if user:
                if not user.is_authenticated:
                    self.fail("user_is_not_authenticated")
                data["creator"] = user.pk
        return super().run_validation(data)

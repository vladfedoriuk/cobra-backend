from typing import Any, Optional

from django.utils.translation import gettext_lazy as _
from djoser.compat import get_user_email_field_name
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from cobra.user.models import CustomUser
from cobra.utils.models import get_object_or_none


class CustomUserSerializer(FlexFieldsModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "full_name",
        )

    def get_full_name(self, obj: CustomUser) -> str:
        return obj.get_full_name()


class ActiveCustomUserRequestedFieldSerializer(serializers.Serializer):
    requested_field: str = "pk"

    default_error_messages = {
        "user_does_not_exist": _("There is no such active user with a given {}").format(
            requested_field
        )
    }

    def initialize_requested_field(self):
        self.fields[self.requested_field] = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_requested_field()

    def validate(self, data: dict[str, Any]):
        validated_data = super().validate(data)
        requested_attr = validated_data.get(self.requested_field)
        user: Optional[CustomUser] = get_object_or_none(
            CustomUser, **{self.requested_field: requested_attr, "is_active": True}
        )
        if user is None or not user.has_usable_password():
            self.fail("user_does_not_exist")
        validated_data["user"] = user
        return validated_data


class ActiveCustomUserUsernameSerializer(ActiveCustomUserRequestedFieldSerializer):
    requested_field: str = CustomUser.USERNAME_FIELD

    default_error_messages = {
        "user_does_not_exist": _("There is no such active user with a given {}").format(
            requested_field
        )
    }


class ActiveCustomUserEmailSerializer(ActiveCustomUserRequestedFieldSerializer):
    requested_field: str = get_user_email_field_name(CustomUser)

    default_error_messages = {
        "user_does_not_exist": _("There is no such active user with a given {}").format(
            requested_field
        )
    }

    def initialize_requested_field(self):
        self.fields[self.requested_field] = serializers.EmailField(required=True)


USER_SEARCH_FIELDS: list[str] = ["username", "email", "first_name", "last_name"]
USER_ORDERING_FIELDS: list[str] = ["username", "email"]

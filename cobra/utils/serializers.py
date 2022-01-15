from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class CustomValidationErrorsMixin:
    default_error_messages: dict[str, str]

    def fail_with_default_error(self, key: str) -> None:
        raise serializers.ValidationError(
            {key: self.default_error_messages.get(key, _("Invalid input data."))}
        )

from typing import TypedDict, cast

from django.contrib.auth.models import AbstractUser
from django.forms import Form
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser


class JWTPair(TypedDict):
    refresh: str
    access: str


class MakeUserFormFieldsRequiredMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in CustomUser.REQUIRED_FIELDS:
            cast(Form, self).fields[field_name].required = True


def get_jwt_tokens_for_user(user: AbstractUser) -> JWTPair:
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

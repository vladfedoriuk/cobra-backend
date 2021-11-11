from typing import TypedDict, cast

from django import template
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.forms import Form
from djoser import utils
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser

register = template.Library()


class JWTPair(TypedDict):
    refresh: str
    access: str


class UIDTokenPair(TypedDict):
    uid: str
    token: str


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


def get_uid_and_token_for_user(user: AbstractUser) -> UIDTokenPair:
    return {
        "uid": utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
    }


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

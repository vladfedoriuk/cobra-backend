from typing import Optional, Union, cast

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.forms import Form
from djoser import utils as djoser_utils
from rest_framework_simplejwt.tokens import RefreshToken

from cobra.utils.test import fake
from cobra.utils.types import JWTPair, UIDTokenPair

from .models import CustomUser


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
        "uid": djoser_utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
    }


USER_CREATE_DATA: dict[str, Optional[Union[str, bool]]] = {
    "username": "test_user",
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "email": fake.email(),
    "password": "pass4test321!",
}

USER_REGISTER_DATA: dict[str, Optional[Union[str, bool]]] = USER_CREATE_DATA | {
    "re_password": USER_CREATE_DATA["password"],
}

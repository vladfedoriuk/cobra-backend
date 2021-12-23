import logging
from typing import Optional, Union, cast

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.forms import Form
from django.utils.translation import gettext_lazy as _
from djoser import utils as djoser_utils
from djoser.conf import settings as djoser_settings
from rest_framework_simplejwt.tokens import RefreshToken

from cobra.services.email.models import TemplateEmail
from cobra.user.models import CustomUser
from cobra.utils.test import fake
from cobra.utils.types import JWTPair, UIDTokenPair

logger = logging.getLogger("django")


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


def get_user_or_none_by_pk(user_pk) -> Optional[AbstractUser]:
    try:
        return CustomUser.objects.get(**{"pk": user_pk})
    except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned):
        logger.error("Failed to get a user by pk=%s", user_pk)
        return None


def get_activation_email_to_user(user: CustomUser) -> TemplateEmail:
    context = {
        "user": user,
        "activation_url": djoser_settings.ACTIVATION_URL.format(
            **get_uid_and_token_for_user(user)
        ),
    }
    to = user.email

    return TemplateEmail(
        subject=_("User activation"),
        mail_from=settings.DEFAULT_FROM_EMAIL,
        mail_to=to,
        template={
            "path": "email/activation.html",
            "context": context,
        },
    )


def get_password_reset_email_to_user(user: CustomUser) -> TemplateEmail:
    context = {
        "user": user,
        "password_reset_url": djoser_settings.PASSWORD_RESET_CONFIRM_URL.format(
            **get_uid_and_token_for_user(user)
        ),
    }
    to = user.email

    return TemplateEmail(
        subject=_("User password reset"),
        mail_from=settings.DEFAULT_FROM_EMAIL,
        mail_to=to,
        template={
            "path": "email/password_reset.html",
            "context": context,
        },
    )

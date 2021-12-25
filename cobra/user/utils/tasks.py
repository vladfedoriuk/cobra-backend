import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from djoser.conf import settings as djoser_settings

from cobra.services.email.models import TemplateEmail
from cobra.user.models import CustomUser
from cobra.user.utils.auth import get_uid_and_token_for_user

logger = logging.getLogger("django")


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

import logging
from typing import Optional

from celery import shared_task

from cobra.services.email.common import send_mail
from cobra.services.email.models import TemplateEmail
from cobra.user.models import CustomUser
from cobra.user.utils.tasks import (
    get_activation_email_to_user,
    get_password_reset_email_to_user,
    get_user_or_none_by_pk,
)

logger = logging.getLogger("celery")


@shared_task
def send_activation_email(user_pk):
    user: Optional[CustomUser] = get_user_or_none_by_pk(user_pk)
    if user is None:
        return

    email: TemplateEmail = get_activation_email_to_user(user)

    logger.info("Sending the activation email to the user with pk=%s", user_pk)

    send_mail(email)


@shared_task
def send_password_reset_email(user_pk):
    user: Optional[CustomUser] = get_user_or_none_by_pk(user_pk)
    if user is None:
        return

    email: TemplateEmail = get_password_reset_email_to_user(user)

    logger.info("Sending the password reset email to the user with pk=%s", user_pk)

    send_mail(email)

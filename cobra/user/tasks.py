import logging

from celery import shared_task
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from djoser.conf import settings as djoser_settings

from cobra.services.email.models import TemplateEmail
from cobra.services.email.services import TemplateEmailService

from .models import CustomUser
from .utils import get_uid_and_token_for_user

logger = logging.getLogger("celery")


@shared_task
def send_activation_email(user_pk):
    try:
        user = CustomUser.objects.get(pk=user_pk)
    except (CustomUser.DoesNotExist, CustomUser.MultipleObjectsReturned) as e:
        logger.error(f"Failed to get a user by pk={user_pk}: {e}")
        return

    context = {
        "user": user,
        "activation_url": djoser_settings.ACTIVATION_URL.format(
            **get_uid_and_token_for_user(user)
        ),
    }
    to = user.email

    template_email = TemplateEmail(
        subject=_("User activation"),
        mail_from=settings.DEFAULT_FROM_EMAIL,
        mail_to=to,
        template={
            "path": "email/activation.html",
            "context": context,
        },
    )
    template_email_service = TemplateEmailService()
    template_email_service.send(template_email)

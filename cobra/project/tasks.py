import logging
from typing import Optional

from celery import shared_task

from cobra.project.models import ProjectInvitation
from cobra.project.utils.tasks import get_project_invitation_email_to_user
from cobra.services.email.common import send_mail
from cobra.services.email.models import TemplateEmail
from cobra.utils.models import get_object_or_none

logger = logging.getLogger("celery")


@shared_task
def send_project_invitation_email(invitation_pk):
    invitation: Optional[ProjectInvitation] = get_object_or_none(
        ProjectInvitation, pk=invitation_pk
    )
    if invitation is None:
        return

    email: TemplateEmail = get_project_invitation_email_to_user(invitation)

    logger.info(
        "Sending the project invitation email to the user with pk=%s",
        invitation.user.pk,
    )

    send_mail(email)

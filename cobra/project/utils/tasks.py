from django.conf import settings
from django.utils.translation import gettext_lazy as _

from cobra.project.models import ProjectInvitation
from cobra.services.email.models import TemplateEmail


def get_project_invitation_email_to_user(
    invitation: ProjectInvitation,
) -> TemplateEmail:
    inviter, user, project = invitation.inviter, invitation.user, invitation.project
    context = {
        "user": user,
        "inviter": inviter,
        "project": project.title,
        "invitation_url": invitation.get_absolute_url(),
    }
    to = user.email

    return TemplateEmail(
        subject=_("Invitation to join a project"),
        mail_from=settings.DEFAULT_FROM_EMAIL,
        mail_to=to,
        template={
            "path": "email/project_invitation.html",
            "context": context,
        },
    )

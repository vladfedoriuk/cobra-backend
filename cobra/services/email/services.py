from typing import Optional, cast

from django.core.mail import EmailMessage

from cobra.services.email.base import BaseEmailService
from cobra.services.email.models import TemplateEmail


class TemplateEmailService(BaseEmailService):
    def send(self, mail: TemplateEmail) -> Optional[EmailMessage]:
        email_message: Optional[EmailMessage]
        if email_message := mail.email:
            email_message.send()
        return cast(Optional[EmailMessage], email_message)

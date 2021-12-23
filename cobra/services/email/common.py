from cobra.services.email.models import TemplateEmail
from cobra.services.email.services import TemplateEmailService


def send_mail(email: TemplateEmail):
    template_email_service = TemplateEmailService()
    template_email_service.send(email)

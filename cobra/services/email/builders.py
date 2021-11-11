from typing import Generic, Optional, Type, TypeVar

from django import forms
from django.core.mail import EmailMessage

from cobra.services.email.base import BaseEmailBuilder, BaseEmailModel

ModelType = TypeVar("ModelType", bound=BaseEmailModel)


class TemplateEmailBuilder(BaseEmailBuilder, Generic[ModelType]):
    class EmailTemplateForm(forms.Form):
        mail_from = forms.EmailField()
        mail_to = forms.EmailField()
        subject = forms.CharField()

    def __get__(
        self, instance: ModelType, owner: Optional[Type[ModelType]] = None
    ) -> Optional[EmailMessage]:
        form_class = self.EmailTemplateForm
        form = form_class(
            data={
                field: getattr(instance, field, None)
                for field in form_class().fields.keys()
            }
        )
        if form.is_valid():
            cd = form.cleaned_data
            msg = EmailMessage(
                subject=cd.get("subject"),
                body=str(instance.content),
                from_email=cd.get("mail_from"),
                to=[cd.get("mail_to")],
                **instance.extra_email_message_kwargs,
            )
            if instance.is_html:
                msg.content_subtype = "html"
            return msg
        return None

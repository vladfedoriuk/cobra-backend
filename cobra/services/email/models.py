from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Optional, TypedDict, Union

from django.http import HttpRequest
from django.template.loader import render_to_string

from cobra.services.email.base import BaseEmailModel
from cobra.services.email.builders import TemplateEmailBuilder


class TemplateParams(TypedDict):
    path: Union[str, Path]
    context: dict[str, Any]


@dataclass
class TemplateEmail(BaseEmailModel):
    subject: str
    mail_from: str
    mail_to: list[str]
    template: TemplateParams
    is_html: bool = True
    request: Optional[HttpRequest] = None
    extra_email_message_kwargs: dict[str, Any] = field(default_factory=dict)

    email: ClassVar[TemplateEmailBuilder] = TemplateEmailBuilder["TemplateEmail"]()

    def get_content(self):
        return render_to_string(
            template_name=self.template.get("path", ""),
            context=self.template.get("context", ""),
            request=self.request,
        )

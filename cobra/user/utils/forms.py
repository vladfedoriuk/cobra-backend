from typing import cast

from django.forms import Form

from cobra.user.models import CustomUser


class MakeUserFormFieldsRequiredMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in CustomUser.REQUIRED_FIELDS:
            cast(Form, self).fields[field_name].required = True

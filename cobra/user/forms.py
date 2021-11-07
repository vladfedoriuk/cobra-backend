from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser
from .utils import MakeUserFormFieldsRequiredMixin


class CustomUserCreationForm(MakeUserFormFieldsRequiredMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            CustomUser.USERNAME_FIELD,
            *CustomUser.REQUIRED_FIELDS,
        )


class CustomUserChangeForm(MakeUserFormFieldsRequiredMixin, UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from cobra.user.models import CustomUser
from cobra.user.utils.forms import MakeUserFormFieldsRequiredMixin


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

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class InactiveUserException(APIException):
    default_code = "inactive_user"
    default_detail = _("The operation was attempted on an inactive user.")
    status_code = status.HTTP_400_BAD_REQUEST

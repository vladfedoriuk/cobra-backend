from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class InvitationIsNotPending(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("The requested project invitation is not pending.")
    default_code = "invitation_is_not_pending"


class UserIsAlreadyMember(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("The user is already a member of the project.")
    default_code = "user_is_already_a_member"


class InvitationHasExpired(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("The invitation has already expired.")
    default_code = "invitation_has_expired"

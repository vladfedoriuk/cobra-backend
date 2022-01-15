from typing import cast

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from djoser import views as djoser_views
from djoser.conf import settings as djoser_settings
from djoser.serializers import (
    ActivationSerializer,
    PasswordResetConfirmRetypeSerializer,
    SendEmailResetSerializer,
    UserCreatePasswordRetypeSerializer,
    UserSerializer,
)
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from cobra.user.api.exceptions import InactiveUserException
from cobra.user.api.serializers.auth.requests import (
    ActivationRequestSerializer,
    RegisterRequestSerializer,
    ResendActivationRequestSerializer,
    ResetPasswordConfirmRequestSerializer,
    ResetPasswordRequestSerializer,
)
from cobra.user.api.serializers.auth.responses import RegisterResponseSerializer
from cobra.user.tasks import send_activation_email, send_password_reset_email
from cobra.utils.swagger import configure_swagger


@configure_swagger
class AuthUserViewSet(djoser_views.UserViewSet):
    swagger_methods_data = {
        "resend_activation": {
            "operation_description": _(
                "Resend the activation code to the inactive user."
            ),
            "request_body": ResendActivationRequestSerializer,
            "responses": {
                status.HTTP_204_NO_CONTENT: openapi.Response(
                    description=_("The activation code has been successfully resent.")
                ),
                status.HTTP_400_BAD_REQUEST: openapi.Response(
                    description=_(
                        "The activation code has not been sent. The user has already been active "
                        "or the email does not exist in the database."
                    ),
                ),
            },
        },
        "activation": {
            "operation_description": _("Activate the inactive user."),
            "request_body": ActivationRequestSerializer,
            "responses": {
                status.HTTP_204_NO_CONTENT: openapi.Response(
                    description=_("The user has been successfully activated.")
                ),
                status.HTTP_400_BAD_REQUEST: openapi.Response(
                    description=_(
                        "The user has not been activated - incorrect token/uid or "
                        "the user has already been activated."
                    ),
                ),
            },
        },
        "reset_password": {
            "operation_description": _("Send a password reset link to the user."),
            "request_body": ResetPasswordRequestSerializer,
            "responses": {
                status.HTTP_204_NO_CONTENT: openapi.Response(
                    description=_("The password reset email has been sent to a user.")
                ),
                status.HTTP_400_BAD_REQUEST: openapi.Response(
                    description=_(
                        "The password reset email has not been sent. "
                        "There is no such user in the database."
                    ),
                ),
            },
        },
        "reset_password_confirm": {
            "operation_description": _("Change a user's password to a new one."),
            "request_body": ResetPasswordConfirmRequestSerializer,
            "responses": {
                status.HTTP_204_NO_CONTENT: openapi.Response(
                    description=_("The password has been changed successfully.")
                ),
                status.HTTP_400_BAD_REQUEST: openapi.Response(
                    description=_(
                        "The password has not been changed successfully - incorrect token/uid or passwords."
                    ),
                ),
            },
        },
        "create": {
            "operation_description": _("Register a new user."),
            "request_body": RegisterRequestSerializer,
            "responses": {
                status.HTTP_201_CREATED: openapi.Response(
                    description=_("An inactive user has been successfully created."),
                    schema=RegisterResponseSerializer,
                ),
                status.HTTP_400_BAD_REQUEST: openapi.Response(
                    description=_(
                        "The user has not been created. Invalid request data."
                    ),
                ),
            },
        },
    }

    def perform_create(self, serializer):
        """
        Copies the original Djoser implementation whereas adding custom
        activation email delivery, and getting rid of
        the confirmation email and signals. Creates a new user in the database.

        :param serializer: Serializer
        :return: None
        """
        user: UserCreatePasswordRetypeSerializer = serializer.save()
        if djoser_settings.SEND_ACTIVATION_EMAIL:
            send_activation_email.apply_async(kwargs={"user_pk": user.pk})

    def perform_update(self, serializer: UserSerializer):
        """
        Overrides the Djoser implementation by sending activation email only to inactive users.
        :param serializer: UserSerializer
        :return: None
        """
        super(djoser_views.UserViewSet, self).perform_update(serializer)
        user = serializer.instance
        if djoser_settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            send_activation_email.apply_async(kwargs={"user_pk": user.pk})

    @action(detail=False, methods=["post"])
    def activation(self, request, *args, **kwargs):
        """
        Copies the original Djoser implementation whereas getting rid of
        the confirmation email and signals. Accepts an uid and a token, and activates the user.

        :param request: HttpRequest
        :param args:
        :param kwargs:
        :return: Response
        """
        serializer: ActivationSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: AbstractUser = serializer.user
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def resend_activation(self, request, *args, **kwargs):
        """
        Copies the original Djoser implementation whereas replacing email
        delivery logic with a custom one. Accepts an email and sends an activation url.

        :param request: HttpRequest
        :param args:
        :param kwargs:
        :return: Response
        """
        serializer: SendEmailResetSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: AbstractUser = serializer.get_user(is_active=False)

        if not djoser_settings.SEND_ACTIVATION_EMAIL or not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        send_activation_email.apply_async(kwargs={"user_pk": user.pk})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def reset_password(self, request, *args, **kwargs):
        """
        Copies the original Djoser implementation whereas replacing email delivery
        logic with a custom one. Accepts an email and sends a password reset url.

        :param request: HttpRequest
        :param args:
        :param kwargs:
        :return: Response
        """
        serializer: SendEmailResetSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: AbstractUser = serializer.get_user()
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        send_password_reset_email.apply_async(kwargs={"user_pk": user.pk})

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["post"])
    def reset_password_confirm(self, request, *args, **kwargs):
        """
        Copies the original Djoser implementation whereas modifying user retrieval process
        and getting rid of session-related logic. Accepts an uid, a new password, and changes
        the user's current password to a new one.

        :param request: HttpRequest
        :param args:
        :param kwargs:
        :return: Response
        """
        serializer: PasswordResetConfirmRetypeSerializer = self.get_serializer(
            data=request.data
        )
        cast(Serializer, serializer).is_valid(raise_exception=True)
        user: AbstractUser = serializer.user
        if not user.is_active:
            raise InactiveUserException(
                detail=_("Inactive users cannot change passwords.")
            )
        validated_data = serializer.validated_data
        user.set_password(validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(status=status.HTTP_204_NO_CONTENT)

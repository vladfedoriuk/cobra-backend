from unittest import mock

from django.conf import settings
from django.test import TestCase
from djoser.conf import settings as djoser_settings

from cobra.user.factories import UserFactory
from cobra.user.models import CustomUser
from cobra.user.tasks import send_activation_email, send_password_reset_email
from cobra.user.utils import get_uid_and_token_for_user


class CeleryTasksTest(TestCase):
    def setUp(self):
        self.user: CustomUser = UserFactory.create()

    @mock.patch("cobra.user.tasks.logger")
    def test_send_activation_email_user_does_not_exist(
        self, mock_logger: mock.MagicMock
    ):
        assert isinstance(self.user.pk, int)
        non_existent_pk: int = (
            max(CustomUser.objects.values_list("id", flat=True)) + 1  # type: ignore
        )
        send_activation_email(non_existent_pk)
        mock_logger.error.assert_called_once_with(
            "Failed to get a user by pk=%s", non_existent_pk
        )

    @mock.patch("cobra.user.tasks.logger")
    @mock.patch("cobra.user.tasks.TemplateEmail")
    @mock.patch("cobra.user.tasks.TemplateEmailService")
    def test_send_activation_email(
        self,
        mock_template_email_service: mock.MagicMock,
        mock_template_email: mock.MagicMock,
        mock_logger: mock.MagicMock,
    ):
        send_activation_email(self.user.pk)
        mock_logger.info.assert_called_once_with(
            "Sending the activation email to the user with pk=%s", self.user.pk
        )
        mock_template_email_service.assert_called_once()
        context = {
            "user": self.user,
            "activation_url": djoser_settings.ACTIVATION_URL.format(
                **get_uid_and_token_for_user(self.user)
            ),
        }
        mock_template_email.assert_called_once_with(
            subject="User activation",
            mail_from=settings.DEFAULT_FROM_EMAIL,
            mail_to=self.user.email,
            template={
                "path": "email/activation.html",
                "context": context,
            },
        )

    @mock.patch("cobra.user.tasks.logger")
    def test_send_password_rest_email_user_does_not_exist(
        self, mock_logger: mock.MagicMock
    ):
        assert isinstance(self.user.pk, int)
        non_existent_pk: int = (
            max(CustomUser.objects.values_list("id", flat=True)) + 1  # type: ignore
        )
        send_password_reset_email(non_existent_pk)
        mock_logger.error.assert_called_once_with(
            "Failed to get a user by pk=%s", non_existent_pk
        )

    @mock.patch("cobra.user.tasks.logger")
    @mock.patch("cobra.user.tasks.TemplateEmail")
    @mock.patch("cobra.user.tasks.TemplateEmailService")
    def test_send_password_reset_email(
        self,
        mock_template_email_service: mock.MagicMock,
        mock_template_email: mock.MagicMock,
        mock_logger: mock.MagicMock,
    ):
        send_password_reset_email(self.user.pk)
        mock_logger.info.assert_called_once_with(
            "Sending the password reset email to the user with pk=%s", self.user.pk
        )
        mock_template_email_service.assert_called_once()
        context = {
            "user": self.user,
            "password_reset_url": djoser_settings.PASSWORD_RESET_CONFIRM_URL.format(
                **get_uid_and_token_for_user(self.user)
            ),
        }
        mock_template_email.assert_called_once_with(
            subject="User password reset",
            mail_from=settings.DEFAULT_FROM_EMAIL,
            mail_to=self.user.email,
            template={
                "path": "email/password_reset.html",
                "context": context,
            },
        )

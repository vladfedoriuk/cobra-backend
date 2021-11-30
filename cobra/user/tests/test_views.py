from collections import ChainMap
from datetime import timedelta
from typing import Any, Optional
from unittest import mock

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import AbstractUser
from django.http import HttpRequest
from django.test import RequestFactory, TestCase, override_settings
from django.urls import path, reverse
from django.utils import timezone
from djoser.conf import settings as djoser_settings
from freezegun import freeze_time
from parameterized import parameterized
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase, URLPatternsTestCase
from rest_framework.views import APIView

from cobra.user.api.views import (
    AuthUserViewSet,
    JWTTokenObtainPairView,
    JWTTokenRefreshView,
    JWTTokenVerifyView,
)
from cobra.user.factories import UserFactory
from cobra.user.models import CustomUser
from cobra.user.utils import JWTPair, UIDTokenPair, fake, get_uid_and_token_for_user

DJOSER: dict[str, Any] = settings.DJOSER


class TestAuthUserViewSet(TestCase):
    default_user_register_data: dict[str, Optional[str]] = {
        "username": "test",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "password": "pass4test321!",
        "re_password": "pass4test321!",
    }

    def setUp(self):
        self.request_factory: RequestFactory = RequestFactory()
        self.register_url: str = reverse("user:api-auth-register")
        self.activation_url: str = reverse("user:api-auth-activate")
        self.resend_activation_url: str = reverse("user:api-auth-activate-resend")
        self.reset_password_url: str = reverse("user:api-auth-reset-password")
        self.reset_password_confirm_url: str = reverse(
            "user:api-auth-reset-password-confirm"
        )
        self.register_view = AuthUserViewSet.as_view({"post": "create"})
        self.activation_view = AuthUserViewSet.as_view({"post": "activation"})
        self.resend_activation_view = AuthUserViewSet.as_view(
            {"post": "resend_activation"}
        )
        self.reset_password_view = AuthUserViewSet.as_view({"post": "reset_password"})
        self.reset_password_confirm_view = AuthUserViewSet.as_view(
            {"post": "reset_password_confirm"}
        )

    @mock.patch("cobra.user.api.views.auth.send_activation_email")
    def test_user_registration(self, mock_send_activation_email: mock.MagicMock):
        user_count = CustomUser.objects.count()
        request: HttpRequest = self.request_factory.post(
            self.register_url, data=self.default_user_register_data
        )
        response: Response = self.register_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_send_activation_email.apply_async.assert_called_once()
        self.assertEqual(CustomUser.objects.count(), user_count + 1)
        user: AbstractUser = CustomUser.objects.get(
            username=self.default_user_register_data.get("username")
        )
        self.assertFalse(user.is_active)

    @override_settings(
        DJOSER=ChainMap(
            {
                "SEND_ACTIVATION_EMAIL": False,
            },
            DJOSER,
        )
    )
    @mock.patch("cobra.user.api.views.auth.send_activation_email")
    def test_register_with_disabled_user_activation_mail(
        self, mock_send_activation_email: mock.MagicMock
    ):
        request: HttpRequest = self.request_factory.post(
            self.register_url, data=self.default_user_register_data
        )
        self.register_view(request)
        self.assertEqual(mock_send_activation_email.call_count, 0)
        user: AbstractUser = CustomUser.objects.get(
            username=self.default_user_register_data.get("username")
        )
        self.assertTrue(user.is_active)

    @parameterized.expand(
        [
            ({}, status.HTTP_201_CREATED, None),
            ({"username": ""}, status.HTTP_400_BAD_REQUEST, "username"),
            ({"first_name": ""}, status.HTTP_400_BAD_REQUEST, "first_name"),
            ({"last_name": ""}, status.HTTP_400_BAD_REQUEST, "last_name"),
            (
                {"password": ""},
                status.HTTP_400_BAD_REQUEST,
                "password",
            ),
            ({"re_password": ""}, status.HTTP_400_BAD_REQUEST, "re_password"),
        ]
    )
    def test_register_responses(self, user_data, response_code, error_field):
        user_data = ChainMap(user_data, self.default_user_register_data)
        with mock.patch("cobra.user.api.views.auth.send_activation_email"):
            request = self.request_factory.post(self.register_url, data=user_data)
            response: Response = self.register_view(request)
            self.assertEqual(response.status_code, response_code)
            if error_field:
                self.assertIn(error_field, response.data)
            else:
                self.assertTrue(
                    CustomUser.objects.filter(
                        username=user_data.get("username")
                    ).exists()
                )
                for field in CustomUser.REQUIRED_FIELDS + [
                    CustomUser.USERNAME_FIELD,
                    djoser_settings.USER_ID_FIELD,
                ]:
                    self.assertIn(field, response.data)

    def test_user_activation_view(self):
        user: CustomUser = UserFactory(is_active=False)

        uid_token: UIDTokenPair = get_uid_and_token_for_user(user)
        request: HttpRequest = self.request_factory.post(
            self.activation_url, data=uid_token
        )
        response: Response = self.activation_view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_user_activation_view_user_is_active(self):
        user: CustomUser = UserFactory()
        self.assertTrue(user.is_active)
        uid_token: UIDTokenPair = get_uid_and_token_for_user(user)
        request: HttpRequest = self.request_factory.post(
            self.activation_url, data=uid_token
        )
        response: Response = self.activation_view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @parameterized.expand(
        [
            (fake.pystr(), None, "invalid_uid"),
            (None, fake.pystr(), "invalid_token"),
        ]
    )
    def test_user_activation_view_responses(self, uid, token, error_code):
        user: CustomUser = UserFactory(is_active=False)
        uid_token: UIDTokenPair = get_uid_and_token_for_user(user)
        uid_token["uid"] = uid or uid_token["uid"]
        uid_token["token"] = token or uid_token["token"]
        request: HttpRequest = self.request_factory.post(
            self.activation_url, data=uid_token
        )
        response: Response = self.activation_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for attr in uid_token.keys():
            self.assertTrue(
                attr not in response.data
                or response.data.get(attr)[0].code == error_code,
                "Received an unexpected error detail in the response.",
            )

    @mock.patch("cobra.user.api.views.auth.send_activation_email")
    def test_user_resend_activation_view(
        self, mock_send_activation_email: mock.MagicMock
    ):
        user: CustomUser = UserFactory(is_active=False)
        request: HttpRequest = self.request_factory.post(
            self.resend_activation_url, data={"email": user.email}
        )
        response: Response = self.resend_activation_view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_send_activation_email.apply_async.assert_called_once_with(
            kwargs={"user_pk": user.pk}
        )

    @override_settings(DJOSER={"SEND_ACTIVATION_EMAIL": False})
    def test_user_resend_activation_view_send_activation_email_disabled(self):
        with mock.patch(
            "cobra.user.api.views.auth.send_activation_email"
        ) as mock_send_activation_email:
            user: CustomUser = UserFactory(is_active=False)
            request: HttpRequest = self.request_factory.post(
                self.resend_activation_url, data={"email": user.email}
            )
            response: Response = self.resend_activation_view(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIsNone(response.data)
            mock_send_activation_email.apply_async.assert_not_called()

    @override_settings(
        DJOSER=ChainMap(
            {
                "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": False,
                "USERNAME_RESET_SHOW_EMAIL_NOT_FOUND": False,
            },
            DJOSER,
        )
    )
    def test_user_resend_activation_view_disable_email_not_found(self):
        with mock.patch(
            "cobra.user.api.views.auth.send_activation_email"
        ) as mock_send_activation_email:
            request: HttpRequest = self.request_factory.post(
                self.resend_activation_url, data={"email": fake.email()}
            )
            response: Response = self.resend_activation_view(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIsNone(response.data)
            mock_send_activation_email.apply_async.assert_not_called()

    @mock.patch("cobra.user.api.views.auth.send_activation_email")
    def test_user_resend_activation_view_responses(self, mock_send_activation_email):
        # Test an active user wishing to resend the activation email.
        user: CustomUser = UserFactory(is_active=True)
        request: HttpRequest = self.request_factory.post(
            self.resend_activation_url, data={"email": user.email}
        )
        response: Response = self.resend_activation_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_send_activation_email.apply_async.assert_not_called()
        self.assertEqual(
            response.data[0].code,
            "email_not_found",
            "Received an unexpected error detail in the response.",
        )

        # Test a non-existent email being provided as an input
        request: HttpRequest = self.request_factory.post(
            self.resend_activation_url, data={"email": fake.email()}
        )
        response: Response = self.resend_activation_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_send_activation_email.apply_async.assert_not_called()
        self.assertEqual(
            response.data[0].code,
            "email_not_found",
            "Received an unexpected error detail in the response.",
        )

    @mock.patch("cobra.user.api.views.auth.send_password_reset_email")
    def test_reset_password_view(self, mock_send_password_reset_email: mock.MagicMock):
        user: CustomUser = UserFactory()
        user.set_password(fake.password())
        request: HttpRequest = self.request_factory.post(
            self.reset_password_confirm_url, data={"email": user.email}
        )
        response: Response = self.reset_password_view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_send_password_reset_email.apply_async.assert_called_once_with(
            kwargs={"user_pk": user.pk}
        )

    @mock.patch("cobra.user.api.views.auth.send_password_reset_email")
    def test_reset_password_view_user_inactive(
        self, mock_send_password_reset_email: mock.MagicMock
    ):
        user: CustomUser = UserFactory(is_active=False)
        request: HttpRequest = self.request_factory.post(
            self.reset_password_confirm_url, data={"email": user.email}
        )
        response: Response = self.reset_password_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_send_password_reset_email.apply_async.assert_not_called()
        self.assertEqual(
            response.data[0].code,
            "email_not_found",
            "Received an unexpected error detail in the response.",
        )

    @mock.patch("cobra.user.api.views.auth.send_password_reset_email")
    def test_reset_password_view_non_existent_email(
        self, mock_send_password_reset_email: mock.MagicMock
    ):
        request: HttpRequest = self.request_factory.post(
            self.reset_password_confirm_url, data={"email": fake.email()}
        )
        response: Response = self.reset_password_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data[0].code,
            "email_not_found",
            "Received an unexpected error detail in the response.",
        )
        mock_send_password_reset_email.apply_async.assert_not_called()

    @override_settings(
        DJOSER=ChainMap(
            {
                "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": False,
                "USERNAME_RESET_SHOW_EMAIL_NOT_FOUND": False,
            },
            DJOSER,
        )
    )
    def test_reset_password_view_disable_email_not_found(self):
        with mock.patch(
            "cobra.user.api.views.auth.send_password_reset_email"
        ) as mock_send_password_reset_email:
            request: HttpRequest = self.request_factory.post(
                self.reset_password_confirm_url, data={"email": fake.email()}
            )
            response: Response = self.reset_password_view(request)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIsNone(response.data)
            mock_send_password_reset_email.apply_async.assert_not_called()

    @parameterized.expand(
        [
            (True, status.HTTP_204_NO_CONTENT),
            (False, status.HTTP_400_BAD_REQUEST),
        ]
    )
    def test_reset_password_confirm_view(self, is_active: bool, response_code: int):
        user: CustomUser = UserFactory(is_active=is_active)
        user.set_password(fake.password())
        user.save(update_fields=["password"])
        user.refresh_from_db()
        uid_token = get_uid_and_token_for_user(user)
        password = fake.password()
        self.assertFalse(check_password(password, user.password))
        data = ChainMap(
            uid_token, {"new_password": password, "re_new_password": password}
        )
        request: HttpRequest = self.request_factory.post(
            self.reset_password_confirm_url, data=data
        )
        response: Response = self.reset_password_confirm_view(request)
        self.assertEqual(response.status_code, response_code)
        user.refresh_from_db()
        if is_active:
            self.assertTrue(check_password(password, user.password))

    @parameterized.expand(
        [
            ({"new_password": fake.password()},),
            ({"re_new_password": fake.password()},),
            ({"uid": fake.pystr()},),
            ({"token": fake.pystr()},),
            *(
                ({key: ""},)
                for key in ["new_password", "re_new_password", "uid", "token"]
            ),
        ]
    )
    def test_reset_password_confirm_view_responses(self, distorted_data):
        user: CustomUser = UserFactory()
        user.set_password(fake.password())
        user.save(update_fields=["password"])
        user.refresh_from_db()
        uid_token = get_uid_and_token_for_user(user)
        password = fake.password()
        self.assertFalse(check_password(password, user.password))
        data = ChainMap(
            distorted_data,
            {
                "new_password": password,
                "re_new_password": password,
                **uid_token,
            },
        )
        request: HttpRequest = self.request_factory.post(
            self.reset_password_confirm_url, data=data
        )
        response: Response = self.reset_password_confirm_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(check_password(password, user.password))


class TestJwtViews(APITestCase, URLPatternsTestCase):
    client: APIClient

    class TestApiView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, *args, **kwargs):
            return Response(status=status.HTTP_204_NO_CONTENT)

    urlpatterns = [
        path(
            "auth/jwt/create/",
            JWTTokenObtainPairView.as_view(),
            name="api-auth-jwt-create",
        ),
        path(
            "auth/jwt/refresh/",
            JWTTokenRefreshView.as_view(),
            name="api-auth-jwt-refresh",
        ),
        path(
            "auth/jwt/verify/",
            JWTTokenVerifyView.as_view(),
            name="api-auth-jwt-verify",
        ),
        path("test/", TestApiView.as_view(), name="api-auth-test"),
    ]

    def setUp(self):
        self.jwt_create_url: str = reverse("api-auth-jwt-create")
        self.jwt_refresh_url: str = reverse("api-auth-jwt-refresh")
        self.jwt_verify_url: str = reverse("api-auth-jwt-verify")
        self.test_endpoint_url: str = reverse("api-auth-test")

    def test_not_authenticated_request(self):
        response: Response = self.client.get(self.test_endpoint_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_authorization(self):
        user: CustomUser = UserFactory()
        password: str = fake.password()
        user.set_password(password)
        user.save()
        response: Response = self.client.post(
            self.jwt_create_url,
            data={
                "username": user.username,
                "password": password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        credentials: JWTPair = response.data
        self.assertIsNotNone(access := credentials.get("access"))
        self.assertIsNotNone(credentials.get("refresh"))
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access}")
        response: Response = self.client.get(self.test_endpoint_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_jwt_refresh(self):
        user: CustomUser = UserFactory()
        password: str = fake.password()
        user.set_password(password)
        user.save()
        response: Response = self.client.post(
            self.jwt_create_url,
            data={
                "username": user.username,
                "password": password,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        credentials: JWTPair = response.data
        self.assertIsNotNone(access := credentials.get("access"))
        self.assertIsNotNone(refresh := credentials.get("refresh"))
        response: Response = self.client.post(
            self.jwt_verify_url,
            data={
                "token": access,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        now = timezone.now()
        token_lifetime: timedelta = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
        with freeze_time(lambda: now + 2 * token_lifetime):
            self._test_refresh_token(access, refresh)

    def _test_refresh_token(self, access, refresh):
        response: Response = self.client.post(
            self.jwt_verify_url,
            data={
                "token": access,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"].code,
            "token_not_valid",
            "The token must be expired.",
        )
        response: Response = self.client.post(
            self.jwt_refresh_url, data={"refresh": refresh}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        credentials: JWTPair = response.data
        self.assertIsNotNone(credentials.get("access"))

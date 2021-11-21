from typing import Optional, Union

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from parameterized import parameterized

from cobra.user.models import CustomUser


class CustomUserManagerTest(TestCase):
    default_user_create_data: dict[str, Optional[Union[str, bool]]] = {
        "username": "test_user",
        "first_name": "Test first name",
        "last_name": "Test last name",
        "email": "test@example.com",
        "password": "pass4test321!",
    }

    @parameterized.expand(
        [
            (default_user_create_data, None),
            (default_user_create_data | {"first_name": None}, ValueError),
            (default_user_create_data | {"last_name": None}, ValueError),
            (default_user_create_data | {"email": None}, ValueError),
            (default_user_create_data | {"username": None}, ValueError),
            (default_user_create_data | {"password": None}, None),
            (
                default_user_create_data | {"is_active": False},
                None,
            ),  # test no implicit is_active setting
        ]
    )
    def test_create_user(self, user_data, exception_class):
        if exception_class:
            with self.assertRaises(exception_class):
                CustomUser.objects.create_user(**user_data)
        else:
            user: CustomUser = CustomUser.objects.create_user(**user_data)
            self.assertEqual(user.is_active, user_data.get("is_active", True))
            if user_password := user_data.get("password"):
                self.assertTrue(check_password(user_password, user.password))
            for field in CustomUser.REQUIRED_FIELDS + [CustomUser.USERNAME_FIELD]:
                self.assertEqual(user_data.get(field), getattr(user, field))

    @parameterized.expand(
        [
            (default_user_create_data, None),
            (default_user_create_data | {"is_active": False}, ValueError),
            (default_user_create_data | {"is_staff": False}, ValueError),
            (default_user_create_data | {"is_superuser": False}, ValueError),
        ]
    )
    def test_create_superuser(self, user_data, exception_class):
        if exception_class:
            with self.assertRaises(exception_class):
                CustomUser.objects.create_superuser(**user_data)
        else:
            superuser: CustomUser = CustomUser.objects.create_superuser(**user_data)
            self.assertTrue(superuser.is_active)
            self.assertTrue(superuser.is_staff)
            self.assertTrue(superuser.is_superuser)

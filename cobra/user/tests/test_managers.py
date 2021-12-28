from collections import ChainMap

from django.contrib.auth.hashers import check_password
from django.test import TestCase
from parameterized import parameterized

from cobra.user.models import CustomUser
from cobra.user.utils.test import USER_CREATE_DATA


class CustomUserManagerTest(TestCase):
    default_user_create_data = USER_CREATE_DATA

    @parameterized.expand(
        [
            ({}, None),
            ({"first_name": None}, ValueError),
            ({"last_name": None}, ValueError),
            ({"email": None}, ValueError),
            ({"username": None}, ValueError),
            ({"password": None}, None),
            (
                {"is_active": False},
                None,
            ),  # tests no enforced is_active setting
        ]
    )
    def test_create_user(self, user_data, exception_class):
        user_data = ChainMap(user_data, self.default_user_create_data)
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
            ({}, None),
            ({"is_active": False}, ValueError),
            ({"is_staff": False}, ValueError),
            ({"is_superuser": False}, ValueError),
        ]
    )
    def test_create_superuser(self, user_data, exception_class):
        user_data = ChainMap(user_data, self.default_user_create_data)
        if exception_class:
            with self.assertRaises(exception_class):
                CustomUser.objects.create_superuser(**user_data)
        else:
            superuser: CustomUser = CustomUser.objects.create_superuser(**user_data)
            self.assertTrue(superuser.is_active)
            self.assertTrue(superuser.is_staff)
            self.assertTrue(superuser.is_superuser)

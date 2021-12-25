from django.db import IntegrityError
from django.test import TestCase

from cobra.user.managers import CustomUserManager
from cobra.user.models import CustomUser
from cobra.utils.test import fake


class CustomUserTest(TestCase):
    def test_required_fields(self):
        for attr in [
            "first_name",
            "last_name",
            "email",
        ]:
            self.assertIn(attr, CustomUser.REQUIRED_FIELDS)

    def test_username(self):
        self.assertEqual(CustomUser.USERNAME_FIELD, "username")

    def test_default_manager(self):
        self.assertTrue(isinstance(CustomUser._default_manager, CustomUserManager))

    def test_email_unique_constraint(self):
        same_email = "test@example.com"
        CustomUser.objects.create(
            username="test_1",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=same_email,
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create(
                username="test_2",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=same_email,
            )

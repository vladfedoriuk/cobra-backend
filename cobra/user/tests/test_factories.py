from django.test import TestCase

from cobra.user.factories import UserFactory
from cobra.user.models import CustomUser
from cobra.user.utils import TestFactoryMixin


class UserFactoryTest(TestCase, TestFactoryMixin):
    factory_class = UserFactory
    must_be_unique = ["username", "email"]
    must_be_not_none = ["username", "email", "first_name", "last_name"]

    def test_create_superuser(self):
        superuser: CustomUser = self.factory_class.create_superuser()
        for attr in [
            "is_active",
            "is_staff",
            "is_superuser",
        ]:
            self.assertTrue(getattr(superuser, attr, None))

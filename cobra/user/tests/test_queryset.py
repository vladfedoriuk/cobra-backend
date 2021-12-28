from django.test import TestCase

from cobra.user.factories import UserFactory
from cobra.user.models import CustomUser


class TestCustomUserQueryset(TestCase):
    def test_filter_admins(self):
        admin: CustomUser = UserFactory.create_superuser()
        user: CustomUser = UserFactory.create()
        admins = CustomUser.objects.all().filter_admins()
        self.assertIn(admin, admins)
        self.assertNotIn(user, admins)

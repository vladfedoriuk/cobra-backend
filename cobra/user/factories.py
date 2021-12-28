import factory
from factory.django import DjangoModelFactory

from cobra.user.models import CustomUser
from cobra.utils.test import fake


class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Sequence(lambda n: "user_%s" % n)
    email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj.username)
    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)

    @classmethod
    def create_superuser(cls, **kwargs):
        kwargs["is_active"] = True
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        return cls.create(**kwargs)

from django.contrib.auth.models import AbstractUser
from django.db.models import Manager

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    objects: Manager["AbstractUser"] = CustomUserManager()  # type: ignore

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    REQUIRED_FIELDS: list[str] = ["first_name", "last_name", "email"]

    email = models.EmailField(
        verbose_name=_("Email"),
        help_text=_(
            "The email will be used for the further user notifications and activation."
        ),
        unique=True,
        max_length=255,
    )

    first_name = models.CharField(_("first name"), max_length=150)  # remove blank=True
    last_name = models.CharField(_("last name"), max_length=150)  # remove blank=True

    objects: Manager["AbstractUser"] = CustomUserManager()  # type: ignore

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def get_default_admin() -> AbstractUser:
    default_admin: dict[str, str] = settings.DEFAULT_ADMIN_INFO
    return get_user_model().objects.get_or_create(
        username=default_admin.get("username"), is_staff=True, is_superuser=True
    )[0]


class TimeStampedModel(models.Model):
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    modified = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        abstract = True


class TimeStampedAndUserRelated(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("user"),
    )

    class Meta:
        abstract = True


class TimeStampedAndOwnedByUser(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_default_admin),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("user"),
    )

    class Meta:
        abstract = True

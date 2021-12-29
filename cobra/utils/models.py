import uuid
from typing import Any, Optional, Union, cast

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager, QuerySet
from django.db.models.base import ModelBase
from django.utils.translation import gettext_lazy as _


def get_default_admin() -> AbstractUser:
    default_admin_info: dict[str, Any] = settings.DEFAULT_ADMIN_INFO
    admin, created = get_user_model().objects.get_or_create(
        username=default_admin_info.get("username"), is_staff=True, is_superuser=True
    )
    if created:
        admin.set_password(default_admin_info.get("password"))
        default_admin_info.pop("password")
        get_user_model().objects.filter(username=admin.username).update(
            **default_admin_info
        )
    return admin


class TimeStampedModel(models.Model):
    created = models.DateTimeField(_("created at"), auto_now_add=True)
    modified = models.DateTimeField(_("modified at"), auto_now=True)

    class Meta:
        abstract = True


class TimeStampedAndRelatedToUser(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("user"),
    )

    class Meta:
        abstract = True


class TimeStampedAndCreatedByUser(TimeStampedModel):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_default_admin),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)s",
        verbose_name=_("creator"),
    )

    class Meta:
        abstract = True


class UUIDPrimaryKeyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


def get_queryset(resource: Union[ModelBase, QuerySet, Manager]) -> QuerySet:
    if hasattr(resource, "_default_manager"):
        queryset: QuerySet = getattr(resource, "_default_manager").all()
        return queryset
    if hasattr(resource, "get"):
        return cast(QuerySet, resource)
    raise TypeError(
        f"The resource must be a Model, Manager, or a QuerySet. Got: {resource}"
    )


def get_object_or_none(
    resource: Union[ModelBase, QuerySet, Manager], *args, **kwargs
) -> Optional[models.Model]:
    queryset = get_queryset(resource)
    try:
        instance: models.Model = queryset.get(*args, **kwargs)
        return instance
    except (queryset.model.DoesNotExist, queryset.model.MultipleObjectsReturned):
        return None

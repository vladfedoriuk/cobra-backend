from typing import Any, Iterable, TypeVar

from django.db import models
from django.utils.text import slugify

ModelType = TypeVar("ModelType", bound=models.Model)


def add_slug_if_not_provided(kwargs: dict[str, Any]):
    kwargs.setdefault("slug", slugify(str(kwargs.get("title"))))
    return kwargs


class ProjectQueryset(models.QuerySet[ModelType]):
    def create(self, **kwargs):
        return super().create(**add_slug_if_not_provided(kwargs))

    def bulk_create(
        self, objects: Iterable[ModelType], batch_size=None, ignore_conflicts=False
    ):
        for obj in objects:
            if not getattr(obj, "slug", ""):
                setattr(obj, "slug", slugify(str(getattr(obj, "title", ""))))
        return super().bulk_create(objects, batch_size, ignore_conflicts)


class ProjectMembershipQueryset(models.QuerySet[ModelType]):
    pass


class EpicQueryset(models.QuerySet[ModelType]):
    pass


class IssueQueryset(models.QuerySet[ModelType]):
    pass

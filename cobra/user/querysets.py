from typing import TypeVar

from django.contrib.auth.models import AbstractUser
from django.db import models

ModelType = TypeVar("ModelType", bound=AbstractUser)


class CustomUserQueryset(models.QuerySet[ModelType]):
    def filter_admins(self):
        return self.filter(is_staff=True, is_superuser=True)

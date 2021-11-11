from abc import ABC, abstractmethod
from functools import cached_property
from typing import Optional

from django.core.mail import EmailMessage


class BaseEmailModel(ABC):
    @abstractmethod
    def get_content(self) -> str:
        ...

    @cached_property
    def content(self) -> str:
        return self.get_content()


class BaseEmailBuilder(ABC):
    @abstractmethod
    def __get__(self, instance, owner=None):
        ...


class BaseEmailService(ABC):
    __instance: Optional["BaseEmailService"] = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @staticmethod
    def send(self, mail: BaseEmailModel) -> Optional[EmailMessage]:
        ...

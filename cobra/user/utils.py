import types
from collections import OrderedDict
from typing import Dict, TypedDict, Union, cast
from unittest import TestCase

from django import template
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.forms import Form
from djoser import utils as djoser_utils
from drf_yasg.utils import swagger_auto_schema
from factory import Factory
from faker import Faker
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser

register = template.Library()


class JWTPair(TypedDict):
    refresh: str
    access: str


class UIDTokenPair(TypedDict):
    uid: str
    token: str


class MakeUserFormFieldsRequiredMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in CustomUser.REQUIRED_FIELDS:
            cast(Form, self).fields[field_name].required = True


def get_jwt_tokens_for_user(user: AbstractUser) -> JWTPair:
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_uid_and_token_for_user(user: AbstractUser) -> UIDTokenPair:
    return {
        "uid": djoser_utils.encode_uid(user.pk),
        "token": default_token_generator.make_token(user),
    }


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


class TestFactoryMixin:
    factory_class: Factory
    batch_size: int = 64
    must_be_unique: list[str] = []
    must_be_not_none: list[str] = []

    @staticmethod
    def attrs_generator_factory(objects: list[models.Model], attr: str):
        return (getattr(obj, attr, None) for obj in objects)

    def test_create_instance(self):
        obj: models.Model = self.factory_class.create()
        cast(TestCase, self).assertIsNotNone(obj)

    def test_create_batch(self):
        objects: list[models.Model] = self.factory_class.create_batch(
            size=self.batch_size
        )
        cast(TestCase, self).assertTrue(all(obj is not None for obj in objects))

    def test_unique_constrains(self):
        objects: list[models.Model] = self.factory_class.create_batch(
            size=self.batch_size
        )
        for attr in self.must_be_unique:
            attrs_set = {self.attrs_generator_factory(objects, attr)}
            attrs_list = [self.attrs_generator_factory(objects, attr)]
            cast(TestCase, self).assertTrue(
                len(set(attrs_set)) == len(list(attrs_list))
            )

    def test_not_none_constrains(self):
        objects: list[models.Model] = self.factory_class.create_batch(
            size=self.batch_size
        )
        for attr in self.must_be_not_none:
            cast(TestCase, self).assertTrue(
                all(x is not None for x in self.attrs_generator_factory(objects, attr))
            )


languages = settings.LANGUAGES

locales: Dict[str, Union[int, float]] = OrderedDict(
    zip(dict(languages).keys(), range(len(languages)))
)

fake = Faker(locales)


def configure_swagger(cls):
    swagger_methods_data = getattr(cls, "swagger_methods_data", {})
    for method_name, data in swagger_methods_data.items():
        if isinstance(method := getattr(cls, method_name), types.FunctionType):
            setattr(cls, method_name, swagger_auto_schema(**data)(method))
    return cls

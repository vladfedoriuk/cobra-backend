from collections import OrderedDict
from typing import Dict, Union, cast
from unittest import TestCase

from django.conf import settings
from django.db import models
from factory import Factory
from faker import Faker


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
            cast(TestCase, self).assertTrue(len(attrs_set) == len(attrs_list))

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

from collections import OrderedDict
from typing import Any, Dict, TypedDict, Union, cast
from unittest import TestCase

from django.conf import settings
from django.db import models
from factory import Factory
from faker import Faker


class PropertyData(TypedDict):
    name: str
    value: Any


class TestFactoryMixin:
    factory_class: Factory
    batch_size: int = 64
    must_be_unique: list[str] = []
    must_be_unique_together: list[str] = []
    must_be_not_none: list[str] = []
    test_with_given_property: list[tuple[PropertyData, Any]] = []

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

    def test_unique_together_constraint(self):
        objects: list[models.Model] = self.factory_class.create_batch(
            size=self.batch_size
        )
        if self.must_be_unique_together:
            attrs_tuple_list: list[tuple[str]] = [
                tuple(
                    str(getattr(obj, attr, None))
                    for attr in self.must_be_unique_together
                )
                for obj in objects
            ]
            cast(TestCase, self).assertEqual(
                len(attrs_tuple_list), len(set(attrs_tuple_list))
            )

    def test_not_none_constrains(self):
        objects: list[models.Model] = self.factory_class.create_batch(
            size=self.batch_size
        )
        for attr in self.must_be_not_none:
            cast(TestCase, self).assertTrue(
                all(x is not None for x in self.attrs_generator_factory(objects, attr))
            )

    def test_with_given(self):
        for given_property, expected in self.test_with_given_property:
            data = {given_property["name"]: given_property["value"]}
            obj = self.factory_class.create(**data)
            cast(TestCase, self).assertEqual(
                getattr(obj, given_property["name"], None), expected
            )


languages = settings.LANGUAGES

locales: Dict[str, Union[int, float]] = OrderedDict(
    zip(dict(languages).keys(), range(len(languages)))
)

fake = Faker(locales)

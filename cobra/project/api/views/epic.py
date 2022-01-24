from typing import cast

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_flex_fields.views import FlexFieldsMixin
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from cobra.project.api.filters import (
    EpicFilter,
    IsEpicProjectMemberOrCreatorFilterBackend,
)
from cobra.project.api.permissions import IsEpicProjectCreator, IsEpicProjectMember
from cobra.project.api.serializers.epic import EpicSerializer
from cobra.project.models import Epic


class GetEpicQuerysetMixin:
    def get_queryset(self) -> QuerySet[Epic]:
        return (
            cast(GenericViewSet, super())
            .get_queryset()
            .select_related("project", "creator")
        )


class EpicUpdateRetrieveViewSet(
    GetEpicQuerysetMixin,
    FlexFieldsMixin,
    GenericViewSet,
    UpdateModelMixin,
    RetrieveModelMixin,
):
    lookup_field = "id"
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    permission_classes = [IsEpicProjectMember | IsEpicProjectCreator]
    filter_backends = [IsEpicProjectMemberOrCreatorFilterBackend]


class EpicListViewSet(
    GetEpicQuerysetMixin, FlexFieldsMixin, GenericViewSet, ListModelMixin
):
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, IsEpicProjectMemberOrCreatorFilterBackend]
    filterset_class = EpicFilter
    permit_list_expands = ["project", "creator"]

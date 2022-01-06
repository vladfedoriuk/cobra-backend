from django_filters.rest_framework import DjangoFilterBackend
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


class EpicUpdateRetrieveViewSet(
    GenericViewSet,
    UpdateModelMixin,
    RetrieveModelMixin,
):
    lookup_field = "id"
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    permission_classes = [IsEpicProjectMember | IsEpicProjectCreator]
    filter_backends = [IsEpicProjectMemberOrCreatorFilterBackend]


class EpicListViewSet(GenericViewSet, ListModelMixin):
    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, IsEpicProjectMemberOrCreatorFilterBackend]
    filterset_class = EpicFilter

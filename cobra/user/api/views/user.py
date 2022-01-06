from rest_flex_fields.views import FlexFieldsMixin
from rest_framework import filters
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from cobra.user.models import CustomUser
from cobra.user.utils.serializers import (
    USER_ORDERING_FIELDS,
    USER_SEARCH_FIELDS,
    CustomUserSerializer,
)


class UserListViewSet(GenericViewSet, ListModelMixin, FlexFieldsMixin):
    queryset = CustomUser.objects.filter(is_active=True)
    serializer_class = CustomUserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = USER_SEARCH_FIELDS
    ordering_fields = USER_ORDERING_FIELDS
    permission_classes = [IsAuthenticated]

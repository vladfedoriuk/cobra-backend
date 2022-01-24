from django.db.models import QuerySet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cobra.project.api.filters import HasAssociatedProjectMembershipFilterBackend
from cobra.project.api.permissions import (
    IsProjectMembershipProjectCreator,
    IsProjectMembershipUserMaintainer,
)
from cobra.project.api.serializers.membership import (
    ProjectMembershipPatchSerializer,
    ProjectMembershipSerializer,
)
from cobra.project.models import ProjectMembership


class ProjectMembershipViewSet(GenericViewSet):
    lookup_field = "id"
    queryset = ProjectMembership.objects.all()
    serializer_class = ProjectMembershipSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [HasAssociatedProjectMembershipFilterBackend]

    def get_queryset(self) -> QuerySet[ProjectMembership]:
        return super().get_queryset().select_related("project", "user")

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[
            IsProjectMembershipUserMaintainer | IsProjectMembershipProjectCreator
        ],
        serializer_class=ProjectMembershipPatchSerializer,
    )
    def change_role(self, *args, **kwargs):
        serializer: ProjectMembershipPatchSerializer = self.get_serializer(
            self.get_object(), data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

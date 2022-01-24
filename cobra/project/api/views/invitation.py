from django.db import transaction
from django.db.models import QuerySet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cobra.project.api.exceptions import (
    InvitationHasExpired,
    InvitationIsNotPending,
    UserIsAlreadyMember,
)
from cobra.project.api.filters import IsInviterOrInvitedUserFilterBackend
from cobra.project.api.permissions import IsInvitedUser
from cobra.project.api.serializers.invitation import ProjectInvitationSerializer
from cobra.project.models import ProjectInvitation, ProjectMembership
from cobra.project.utils.models import ACCEPTED, REJECTED


class ProjectInvitationViewSet(RetrieveModelMixin, GenericViewSet):
    lookup_field = "id"
    queryset = ProjectInvitation.objects.all()
    serializer_class = ProjectInvitationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [IsInviterOrInvitedUserFilterBackend]

    def get_queryset(self) -> QuerySet[ProjectInvitation]:
        return super().get_queryset().select_related("user", "inviter", "project")

    @action(detail=True, methods=["post"], permission_classes=[IsInvitedUser])
    def accept(self, *args, **kwargs):
        invitation: ProjectInvitation = self.get_object()
        if not invitation.is_pending:
            raise InvitationIsNotPending()
        if invitation.is_expired:
            raise InvitationHasExpired()
        if ProjectMembership.objects.filter(
            user__pk=invitation.user.pk, project__pk=invitation.project.pk
        ).exists():
            raise UserIsAlreadyMember()
        with transaction.atomic():
            ProjectMembership.objects.create(
                user=invitation.user, project=invitation.project
            )
            invitation.status = ACCEPTED
            invitation.save(update_fields=["status"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsInvitedUser])
    def reject(self, *args, **kwargs):
        invitation: ProjectInvitation = self.get_object()
        if not invitation.is_pending:
            raise InvitationIsNotPending()
        if invitation.is_expired:
            raise InvitationHasExpired()
        if ProjectMembership.objects.filter(
            user__pk=invitation.user.pk, project__pk=invitation.project.pk
        ).exists():
            raise UserIsAlreadyMember()
        invitation.status = REJECTED
        invitation.save(update_fields=["status"])
        return Response(status=status.HTTP_204_NO_CONTENT)

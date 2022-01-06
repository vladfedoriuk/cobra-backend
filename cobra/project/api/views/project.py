from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cobra.project.api.filters import IsProjectMemberOrCreatorFilterBackend
from cobra.project.api.permissions import (
    CustomIsAdminUser,
    IsProjectCreator,
    IsProjectMaintainer,
    IsProjectMember,
    IsProjectMemberAndReadOnly,
)
from cobra.project.api.serializers.epic import EpicSerializer
from cobra.project.api.serializers.invitation import ProjectInvitationSerializer
from cobra.project.api.serializers.issue import IssueSerializer
from cobra.project.api.serializers.membership import ProjectMembershipSerializer
from cobra.project.api.serializers.project import ProjectSerializer
from cobra.project.models import (
    Epic,
    Issue,
    Project,
    ProjectInvitation,
    ProjectMembership,
)
from cobra.user.utils.serializers import ActiveCustomUserEmailSerializer


class ProjectViewSet(FlexFieldsModelViewSet):
    permit_list_expands = ["creator", "members", "project"]
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [IsProjectMemberOrCreatorFilterBackend]

    def get_permissions(self):
        if self.action in ("retrieve", "list"):
            self.permission_classes = [
                CustomIsAdminUser | IsProjectCreator | IsProjectMemberAndReadOnly
            ]
        elif self.action in (
            "update",
            "partial_update",
        ):
            self.permission_classes = [
                CustomIsAdminUser | IsProjectCreator | IsProjectMaintainer
            ]
        elif self.action in ("destroy",):
            self.permission_classes = [CustomIsAdminUser | IsProjectCreator]
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            context["project"] = self.get_object()
        return context

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[
            CustomIsAdminUser | IsProjectCreator | IsProjectMemberAndReadOnly
        ],
        serializer_class=ProjectMembershipSerializer,
    )
    def memberships(self, *args, **kwargs):
        project: Project = self.get_object()
        memberships = ProjectMembership.objects.filter(project__pk=project.pk)
        serializer = self.get_serializer(memberships, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsProjectCreator | IsProjectMaintainer],
        serializer_class=ProjectInvitationSerializer,
    )
    def invitations(self, *args, **kwargs):
        user_serializer = ActiveCustomUserEmailSerializer(data=self.request.data)
        user_serializer.is_valid(raise_exception=True)
        data = {"user": getattr(user_serializer.validated_data.get("user"), "pk", None)}
        serializer: ProjectInvitationSerializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance: ProjectInvitation = serializer.save()
        instance.send()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post", "get"],
        permission_classes=[IsProjectMember | IsProjectCreator],
        serializer_class=EpicSerializer,
    )
    def epics(self, *args, **kwargs):
        if self.request.method == "POST":
            serializer: EpicSerializer = self.get_serializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == "GET":
            serializer: EpicSerializer = self.get_serializer(
                Epic.objects.filter(project=self.get_object()), many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post", "get"],
        permission_classes=[IsProjectMember | IsProjectCreator],
        serializer_class=IssueSerializer,
    )
    def issues(self, *args, **kwargs):
        if self.request.method == "POST":
            serializer: IssueSerializer = self.get_serializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif self.request.method == "GET":
            serializer: IssueSerializer = self.get_serializer(
                Issue.objects.filter(project=self.get_object()), many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)

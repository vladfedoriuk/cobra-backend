from django_filters.rest_framework import DjangoFilterBackend
from rest_flex_fields.views import FlexFieldsMixin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cobra.project.api.filters import (
    IsIssueProjectMemberOrCreatorFilterBackend,
    IssueFilter,
)
from cobra.project.api.permissions import IsIssueProjectCreator, IsIssueProjectMember
from cobra.project.api.serializers.comment import IssueCommentSerializer
from cobra.project.api.serializers.issue import IssueSerializer
from cobra.project.api.serializers.logged_time import LoggedTimeSerializer
from cobra.project.models import Issue
from cobra.project.utils.types import HTTP_METHODS


class IssueUpdateRetrieveViewSet(
    FlexFieldsMixin,
    GenericViewSet,
    UpdateModelMixin,
    RetrieveModelMixin,
):
    lookup_field = "id"
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsIssueProjectCreator | IsIssueProjectMember]
    filter_backends = [IsIssueProjectMemberOrCreatorFilterBackend]

    permit_list_expands = ["parent", "project", "creator", "assignee"]

    LOGGED_TIME_METHODS: HTTP_METHODS = ["get", "post"]
    COMMENTS_METHODS = LOGGED_TIME_METHODS
    SUBISSUES_METHODS: HTTP_METHODS = ["get"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in self.kwargs:
            context["issue"] = self.get_object()
        return context

    def get_permissions(self):
        if self.action in ("logged_time", "comments") and self.request.method == "GET":
            self.permission_classes = [IsIssueProjectMember | IsIssueProjectCreator]
        return super().get_permissions()

    @action(
        detail=True,
        methods=LOGGED_TIME_METHODS,
        serializer_class=LoggedTimeSerializer,
        permission_classes=[IsIssueProjectMember],
    )
    def logged_time(self, *args, **kwargs):
        if self.request.method == "GET":
            issue = self.get_object()
            serializer = self.get_serializer(
                issue.project_loggedtime_related.all(), many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        if self.request.method == "POST":
            serializer = self.get_serializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=COMMENTS_METHODS,
        serializer_class=IssueCommentSerializer,
        permission_classes=[IsIssueProjectMember],
    )
    def comments(self, *args, **kwargs):
        if self.request.method == "GET":
            issue = self.get_object()
            serializer = self.get_serializer(
                issue.project_issuecomment_related.all(), many=True
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        if self.request.method == "POST":
            serializer = self.get_serializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=SUBISSUES_METHODS,
        permission_classes=[IsIssueProjectMember],
    )
    def sub_issues(self, *args, **kwargs):
        sub_issues = self.get_object().child_issues.all()
        serializer = self.get_serializer(sub_issues, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class IssueListViewSet(GenericViewSet, ListModelMixin):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, IsIssueProjectMemberOrCreatorFilterBackend]
    filterset_class = IssueFilter

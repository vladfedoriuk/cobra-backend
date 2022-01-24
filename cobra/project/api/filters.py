import django_filters.rest_framework
from django.db.models import Q
from rest_framework import filters

from cobra.project.models import Epic, Issue, Project, ProjectMembership


class IsProjectMemberOrCreatorFilterBackend(filters.BaseFilterBackend):
    """
    Filter that grants access only to the project members or creators
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_staff and user.is_authenticated:
            user_pk = user.pk
            queryset = queryset.filter(
                Q(creator__pk=user_pk) | Q(members__pk__in=[user_pk])
            )
        return queryset.distinct()


class IsInviterOrInvitedUserFilterBackend(filters.BaseFilterBackend):
    """
    Filter that grants access only to the project inviters or invited users
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_staff and user.is_authenticated:
            queryset = queryset.filter(Q(user__pk=user.pk) | Q(inviter__pk=user.pk))
        return queryset.distinct()


class HasAssociatedProjectMembershipFilterBackend(filters.BaseFilterBackend):
    """
    Filter that grants access only to the project memberships associated to a user
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_staff and user.is_authenticated:
            user_projects = ProjectMembership.objects.filter(
                user__pk=user.pk
            ).values_list("project", flat=True)
            return queryset.filter(project__pk__in=user_projects)
        return queryset.distinct()


class IsIssueProjectMemberOrCreatorFilterBackend(filters.BaseFilterBackend):
    """
    Filter that grants access only to the issues that belong to the projects the user is a member of.
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_staff and user.is_authenticated:
            user_projects = Project.objects.filter(
                Q(members__pk__in=[user.pk]) | Q(creator__pk=user.pk)
            )
            queryset = queryset.filter(project__pk__in=user_projects)
        return queryset.distinct()


class IsEpicProjectMemberOrCreatorFilterBackend(filters.BaseFilterBackend):
    """
    Filter that grants access only to the issues that belong to the projects the user is a member of.
    """

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_staff and user.is_authenticated:
            user_projects = Project.objects.filter(
                Q(members__pk__in=[user.pk]) | Q(creator__pk=user.pk)
            )
            queryset = queryset.filter(project__pk__in=user_projects)
        return queryset.distinct()


class IssueFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Issue
        fields = ("type", "project", "epic")


class EpicFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Epic
        fields = ("project",)

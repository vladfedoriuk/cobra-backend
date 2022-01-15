from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from cobra.project.models import (
    Epic,
    Issue,
    Project,
    ProjectInvitation,
    ProjectMembership,
)
from cobra.project.utils.models import MAINTAINER


class CustomIsAdminUser(IsAdminUser):
    def has_object_permission(self, request, view, obj) -> bool:
        """
        https://stackoverflow.com/questions/67679870/django-rest-permission-classes-dont-work-together-inside-an-or-"
        "but-work-as-expe"

        This function overrides the default has_object_permission to prevent the bug documented in:
        https://github.com/encode/django-rest-framework/issues/7117
        """

        return self.has_permission(request, view)


class IsProjectCreator(IsAuthenticated):
    message = _(
        "Access to the information of the project is granted only to the creators."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: Project
    ) -> bool:
        """
        Only the creator of the project can have access to it.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return obj.creator == request.user


class IsProjectMembershipProjectCreator(IsAuthenticated):
    message = _(
        "Access to the information of the project memberships is granted only to the creators."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: ProjectMembership
    ) -> bool:
        """
        Only the creator of the project can have access to its project memberships.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return obj.project.creator == request.user


class IsEpicProjectCreator(IsAuthenticated):
    message = _(
        "Access to the information of the epic  is granted only to the creators of the project epic belongs to."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request: Request, view: APIView, obj: Epic) -> bool:
        """
        Only the creator of the project can have access to its epics.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return bool(obj.project.creator == request.user)


class IsIssueProjectCreator(IsAuthenticated):
    message = _(
        "Access to the information of the issue  is granted only to the creators of the project issue belongs to."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: Issue
    ) -> bool:
        """
        Only the creator of the project can have access to its epics.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return bool(obj.project.creator == request.user)


class IsProjectMember(IsAuthenticated):
    message = _(
        "Access to the information of the project is granted only to the members."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: Project
    ) -> bool:
        """
        Only the project members can have access to the project.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return obj.members.all().filter(pk=request.user.pk).exists()


class IsEpicProjectMember(IsAuthenticated):
    message = _(
        "Access to the information of the epic is granted only to the epic's project members."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(self, request: Request, view: APIView, obj: Epic) -> bool:
        """
        Only the project members can have access to the project.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return bool(obj.project.members.all().filter(pk=request.user.pk).exists())


class IsIssueProjectMember(IsAuthenticated):
    message = _(
        "Access to the information of the issue is granted only to the issue's project members."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: Issue
    ) -> bool:
        """
        Only the project members can have access to the project.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return bool(obj.project.members.all().filter(pk=request.user.pk).exists())


class IsProjectMemberAndReadOnly(IsProjectMember):
    message = _(
        "Access to the information of the project is granted only to the members. The members can only read data."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: Project
    ) -> bool:
        """
        Only the project members can modify to the project.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return (
            super().has_object_permission(request, view, obj)
            and request.method in SAFE_METHODS
        )


class IsProjectMaintainer(IsAuthenticated):
    message = _(
        "Access to the information of the project is granted only to the maintainers."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: Project
    ) -> bool:
        """
        Only the project maintainers can have access to the project.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return ProjectMembership.objects.filter(
            user__pk=request.user.pk, project__pk=obj.pk, role=MAINTAINER
        ).exists()


class IsProjectMembershipUserMaintainer(IsAuthenticated):
    message = _(
        "Access to the information of the project memberships is granted only to the project maintainers."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: ProjectMembership
    ) -> bool:
        """
        Only the project maintainers can have access to the project memberships.

        :param request: Request
        :param view: APIView
        :param obj: Project
        :return: bool
        """
        return ProjectMembership.objects.filter(
            user__pk=request.user.pk, project__pk=obj.project.pk, role=MAINTAINER
        ).exists()


class IsInvitedUser(IsAuthenticated):
    message = _(
        "Access to the information of the invitation is granted only to the invited user."
    )
    code = status.HTTP_403_FORBIDDEN

    def has_object_permission(
        self, request: Request, view: APIView, obj: ProjectInvitation
    ) -> bool:
        return request.user == obj.user

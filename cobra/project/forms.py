from collections import defaultdict
from typing import Optional

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from cobra.project.models import (
    Epic,
    Issue,
    Project,
    ProjectInvitation,
    ProjectMembership,
)
from cobra.project.utils.models import BUG, TASK, TASK_TYPES, USER_STORY
from cobra.user.models import CustomUser


class ExcludeDatesMeta:
    exclude = ["created", "modified"]


class ProjectAdminForm(forms.ModelForm):
    class Meta(ExcludeDatesMeta):
        model = Project


class ProjectInvitationAdminForm(forms.ModelForm):
    class Meta(ExcludeDatesMeta):
        model = ProjectInvitation
        labels = {
            "user": _("Invited user"),
        }

    def clean(self):
        cleaned_data = super().clean()
        inviter: CustomUser = cleaned_data.get("inviter")
        project: Project = cleaned_data.get("project")
        if not ProjectMembership.objects.is_user_project_maintainer_or_creator(
            inviter, project
        ):
            self.add_error(
                "inviter",
                ValidationError(
                    _(
                        "The inviter must be a maintainer or the creator of the project to be able to invite new users."
                    )
                ),
            )
        return cleaned_data


class ProjectMembershipAdminForm(forms.ModelForm):
    class Meta(ExcludeDatesMeta):
        model = ProjectMembership


class EpicAdminForm(forms.ModelForm):
    class Meta(ExcludeDatesMeta):
        model = Epic

    def clean(self):
        cleaned_data = super().clean()
        creator: CustomUser = cleaned_data.get("creator")
        project: Project = cleaned_data.get("project")
        if not ProjectMembership.objects.is_user_project_member_or_creator(
            creator, project
        ):
            self.add_error(
                "creator",
                ValidationError(
                    _("The creator must be a member of the project or its creator.")
                ),
            )
        return cleaned_data


class IssueAdminForm(forms.ModelForm):
    class Meta(ExcludeDatesMeta):
        model = Issue
        error_messages = {
            "assignee": {
                "assignee_project_relation": _(
                    "The assignee must be a member of the project the issue belongs to."
                )
            },
            "epic": {
                "epic_project_relation": _(
                    "The epic must belong to the same project as the issue."
                )
            },
            "parent": {
                "parent_project_relation": _(
                    "The parent issue must belong to the same project as the issue."
                )
            },
            "creator": {
                "creator_project_relation": _(
                    "The creator must be a member or the creator of the issue's project."
                )
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound and self.instance.pk:
            self.fields["assignee"].queryset = self.instance.project.members.all()
            self.fields["parent"].queryset = Issue.objects.filter(
                project__pk=self.instance.project.pk
            ).exclude(pk=self.instance.pk)
            self.fields["epic"].queryset = Epic.objects.filter(
                project__pk=self.instance.project.pk
            )
            self.fields["creator"].queryset = CustomUser.objects.filter(
                Q(project__pk__in=[self.instance.project.pk])
                | Q(pk=self.instance.project.creator.pk)
            ).distinct()

    def clean(self):
        error_messages = getattr(
            getattr(self, "_meta", None),
            "error_messages",
            defaultdict(lambda: defaultdict(lambda: "error")),
        )
        cleaned_data = super().clean()
        project: Optional[Project] = cleaned_data.get("project")
        parent: Optional[Issue] = cleaned_data.get("parent")
        epic: Optional[Epic] = cleaned_data.get("epic")
        assignee: Optional[CustomUser] = cleaned_data.get("assignee")
        creator: Optional[CustomUser] = cleaned_data.get("creator")
        if (
            project
            and creator
            and not ProjectMembership.objects.is_user_project_member_or_creator(
                creator, project
            )
        ):
            self.add_error(
                key := "creator",
                error_messages[key]["creator_project_relation"],
            )
        if (
            project
            and assignee
            and not ProjectMembership.objects.is_user_project_member(assignee, project)
        ):
            self.add_error(
                key := "assignee",
                error_messages[key]["assignee_project_relation"],
            )
        if project and epic and epic.project != project:
            self.add_error(key := "epic", error_messages[key]["epic_project_relation"])
        if project and parent and parent.project != project:
            self.add_error(
                key := "parent", error_messages[key]["parent_project_relation"]
            )
        return cleaned_data


class TaskAdminForm(IssueAdminForm):
    class Meta(IssueAdminForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].limit_choices_to = tuple(
            filter(lambda x: x[0] == TASK, TASK_TYPES)
        )


class BugAdminForm(IssueAdminForm):
    class Meta(IssueAdminForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].limit_choices_to = tuple(
            filter(lambda x: x[0] == BUG, TASK_TYPES)
        )


class UserStoryAdminForm(IssueAdminForm):
    class Meta(IssueAdminForm.Meta):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["type"].limit_choices_to = tuple(
            filter(lambda x: x[0] == USER_STORY, TASK_TYPES)
        )

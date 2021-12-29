from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from cobra.project.models import Project, ProjectInvitation, ProjectMembership
from cobra.project.utils.models import MAINTAINER
from cobra.user.models import CustomUser


class ExcludeDatesMeta:
    exclude = ["created", "modified"]


class ProjectAdminForm(forms.ModelForm):
    class Meta(ExcludeDatesMeta):
        model = Project

    def clean(self):
        cleaned_data = super().clean()
        user: CustomUser = cleaned_data.get("creator")
        slug: Project = cleaned_data.get("slug")
        if Project.objects.filter(creator=user, slug=slug).exists():
            raise ValidationError(
                _(
                    "There is already a project with such a slug belonging to the given user"
                )
            )


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
        if not (
            ProjectMembership.objects.filter(
                user=inviter, role=MAINTAINER, project=project
            ).exists()
            or project.creator == inviter
        ):
            self.add_error(
                "inviter",
                ValidationError(
                    _(
                        "The inviter must be a maintainer or the creator of the project to be able to invite new users."
                    )
                ),
            )

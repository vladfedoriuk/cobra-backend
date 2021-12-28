from django import forms

from cobra.project.models import Project


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ["created", "modified"]

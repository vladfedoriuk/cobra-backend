from typing import Type

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from cobra.project.forms import (
    BugAdminForm,
    EpicAdminForm,
    IssueAdminForm,
    ProjectAdminForm,
    ProjectInvitationAdminForm,
    ProjectMembershipAdminForm,
    TaskAdminForm,
    UserStoryAdminForm,
)
from cobra.project.models import (
    Bug,
    Epic,
    Issue,
    IssueComment,
    LoggedTime,
    Project,
    ProjectInvitation,
    ProjectMembership,
    Task,
    UserStory,
)
from cobra.project.utils.models import BUG, TASK, TASK_TYPES, USER_STORY


class CustomUserListFilter(admin.SimpleListFilter):
    title = _("user")
    parameter_name = "user"

    def lookups(self, request, model_admin):
        yield from [
            (str(obj.pk), obj.get_full_name()) for obj in get_user_model().objects.all()
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__pk=self.value())


class ProjectListFilter(admin.SimpleListFilter):
    title = _("project")
    parameter_name = "project"

    def lookups(self, request, model_admin):
        yield from [(str(obj.pk), str(obj)) for obj in Project.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(project__pk=self.value())


class IssueInline(admin.StackedInline):
    model = Issue
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "project":
            if parent_obj := getattr(self, "parent_obj", None):
                kwargs["queryset"] = Project.objects.filter(pk=parent_obj.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        setattr(self, "parent_obj", obj)
        return super().get_formset(request, obj, **kwargs)


class CreatorListFilter(CustomUserListFilter):
    title = _("Creator")
    parameter_name = "creator"


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1


class ProjectMembershipAdmin(admin.ModelAdmin):
    add_form = ProjectMembershipAdminForm
    list_display = ("id", "user_full_name", "project", "role")
    list_filter = ("project", "role", "modified", "created", CustomUserListFilter)
    search_fields = ("project", "user")
    raw_id_fields = ("project", "user")
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "project",
                    "role",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    @admin.display(description=_("User"), ordering="user")
    def user_full_name(self, obj):
        return obj.user.get_full_name()


class EpicAdmin(admin.ModelAdmin):
    form = EpicAdminForm
    list_display = (
        "id",
        "title",
        "user_full_name",
        "project",
    )
    list_filter = ("modified", "created", CustomUserListFilter, ProjectListFilter)
    search_fields = ("project", "creator", "title", "description")
    raw_id_fields = ("project", "creator")
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")

    inlines = (IssueInline,)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "creator",
                    "project",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    @admin.display(description=_("Creator"), ordering="creator")
    def user_full_name(self, obj):
        return obj.creator.get_full_name()


class AssigneeListFilter(CustomUserListFilter):
    title = _("Assignee")
    parameter_name = "assignee"


class IssueAdmin(admin.ModelAdmin):
    form: Type[forms.ModelForm] = IssueAdminForm
    list_display = (
        "id",
        "title",
        "project",
        "creator_full_name",
        "assignee_full_name",
    )
    list_filter = (
        "created",
        "modified",
        CreatorListFilter,
        AssigneeListFilter,
        ProjectListFilter,
    )
    search_fields = ("title", "creator", "assignee", "project")
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "creator",
                    "assignee",
                ),
            },
        ),
        (
            _("State"),
            {
                "fields": (
                    "status",
                    "type",
                    "estimate",
                ),
            },
        ),
        (
            _("Relationships"),
            {
                "fields": (
                    "parent",
                    "epic",
                    "project",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    def get_form(self, request, obj=None, **kwargs):
        setattr(self, "issue_obj", obj)
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if issue_obj := getattr(self, "issue_obj", None):
            if db_field.name == "assignee":
                kwargs["queryset"] = issue_obj.project.members.all()
            if db_field.name == "parent":
                kwargs["queryset"] = Issue.objects.filter(
                    project__pk=issue_obj.project.pk
                ).exclude(pk=issue_obj.pk)
            if db_field.name == "epic":
                kwargs["queryset"] = Epic.objects.filter(
                    project__pk=issue_obj.project.pk
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description=_("Creator"), ordering="creator")
    def creator_full_name(self, obj):
        return obj.creator.get_full_name()

    @admin.display(description=_("Assignee"), ordering="assignee")
    def assignee_full_name(self, obj):
        return obj.assignee.get_full_name() if obj.assignee else ""


class TaskAdmin(IssueAdmin):
    form = TaskAdminForm

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["choices"] = tuple(filter(lambda x: x[0] == TASK, TASK_TYPES))
        return super().formfield_for_choice_field(db_field, request, **kwargs)


class BugAdmin(IssueAdmin):
    form = BugAdminForm

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["choices"] = tuple(filter(lambda x: x[0] == BUG, TASK_TYPES))
        return super(admin.ModelAdmin, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )


class UserStoryAdmin(IssueAdmin):
    form = UserStoryAdminForm

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "type":
            kwargs["choices"] = tuple(filter(lambda x: x[0] == USER_STORY, TASK_TYPES))
        return super(admin.ModelAdmin, self).formfield_for_choice_field(
            db_field, request, **kwargs
        )


class ProjectAdmin(admin.ModelAdmin):
    add_form = ProjectAdminForm
    list_display = ("id", "title", "slug", "creator_full_name")
    list_filter = ("title", "created", "modified", CreatorListFilter)
    search_fields = ("title", "creator")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("creator",)
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "description",
                    "creator",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    inlines = (ProjectMembershipInline,)

    @admin.display(description=_("Creator"), ordering="creator")
    def creator_full_name(self, obj):
        return obj.creator.get_full_name()


class ProjectInvitationAdmin(admin.ModelAdmin):
    form = ProjectInvitationAdminForm
    list_display = (
        "user_full_name",
        "inviter_full_name",
        "project",
        "status",
        "is_active",
    )
    list_filter = ("status", "created", "modified", CustomUserListFilter, "project")
    search_fields = ("user", "project")
    raw_id_fields = ("user", "project")
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")
    actions = ["send_invitations"]

    @admin.action(description=_("Send the selected invitations to the users"))
    def send_invitations(self, request: HttpRequest, queryset: QuerySet):
        for obj in queryset:
            obj.send()
        self.message_user(
            request,
            ngettext(
                "%d invitation has been sent to a user.",
                "%d invitations have been sent to the users.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "status",
                    "project",
                    "user",
                    "inviter",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    @admin.display(description=_("User"), ordering="user")
    def user_full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description=_("Inviter"), ordering="inviter")
    def inviter_full_name(self, obj):
        return obj.inviter.get_full_name()

    @admin.display(boolean=True, ordering="-created", description="Is active?")
    def is_active(self, obj):
        return not obj.is_expired


class LoggedTimeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_full_name",
        "issue",
        "time",
    )
    list_filter = ("created", "modified", CustomUserListFilter, "issue")
    search_fields = ("user", "issue")
    raw_id_fields = ("user", "issue")
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "issue",
                    "user",
                    "time",
                    "comment",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    @admin.display(description=_("User"), ordering="user")
    def user_full_name(self, obj):
        return obj.user.get_full_name()


class TaskCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_full_name",
        "issue",
    )
    list_filter = ("created", "modified", CustomUserListFilter, "issue")
    search_fields = ("user", "issue", "content")
    raw_id_fields = ("user", "issue")
    date_hierarchy = "created"
    ordering = ("-modified", "created")
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "issue",
                    "user",
                    "content",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    @admin.display(description=_("User"), ordering="user")
    def user_full_name(self, obj):
        return obj.user.get_full_name()


admin.site.register(IssueComment, TaskCommentAdmin)
admin.site.register(LoggedTime, LoggedTimeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Bug, BugAdmin)
admin.site.register(UserStory, UserStoryAdmin)
admin.site.register(Epic, EpicAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectInvitation, ProjectInvitationAdmin)
admin.site.register(ProjectMembership, ProjectMembershipAdmin)

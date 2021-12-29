from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from cobra.project.forms import ProjectAdminForm, ProjectInvitationAdminForm
from cobra.project.models import Project, ProjectInvitation


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


class CreatorListFilter(CustomUserListFilter):
    title = _("Creator")
    parameter_name = "creator"


class ProjectAdmin(admin.ModelAdmin):
    add_form = ProjectAdminForm
    list_display = ("title", "slug", "creator_full_name")
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
                    "creator",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

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


admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectInvitation, ProjectInvitationAdmin)

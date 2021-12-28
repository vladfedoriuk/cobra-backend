from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from cobra.project.forms import ProjectAdminForm
from cobra.project.models import Project


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


class ProjectAdmin(admin.ModelAdmin):
    add_form = ProjectAdminForm
    list_display = ("title", "slug", "user_full_name")
    list_filter = ("title", "created", "modified", CustomUserListFilter)
    search_fields = ("title", "user")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("user",)
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
                    "user",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("created", "modified")}),
    )

    @admin.display(description=_("User"), ordering="user")
    def user_full_name(self, obj):
        return obj.user.get_full_name()


admin.site.register(Project, ProjectAdmin)

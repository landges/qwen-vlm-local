from django.contrib import admin

from .models import MemorySpace, PersonalAccessToken, Project


@admin.register(MemorySpace)
class MemorySpaceAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "owner__username")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    filter_horizontal = ("members",)


@admin.register(PersonalAccessToken)
class PersonalAccessTokenAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "scope_type",
        "project",
        "memory_space",
        "prefix",
        "can_read",
        "can_write",
        "created_at",
        "last_used_at",
        "revoked_at",
    )
    list_filter = ("scope_type", "can_read", "can_write", "revoked_at")
    search_fields = (
        "name", "user__username", "prefix", "project__slug", "memory_space__name"
    )
    readonly_fields = (
        "id",
        "secret_digest",
        "prefix",
        "created_at",
        "last_used_at",
    )

from django.contrib import admin

from .models import Member, Organization, WorkSpace


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'owner', 'created_at')
    readonly_fields = ('id', 'created_at')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('user', 'organization', 'role', 'last_activity')
    list_filter = ('role', 'organization')
    readonly_fields = ('id', 'created_at')


@admin.register(WorkSpace)
class WorkspaceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'space_code', 'organization', 'created_by')
    readonly_fields = ('id', 'created_at')

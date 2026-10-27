from typing import override

from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest

from organizations.mailpitRequests.emails import InvitationEmailError, send_invitation_email

from .models import Member, Organization, OrgInvitation, WorkSpace


class WorkspaceInline(admin.TabularInline[WorkSpace, Organization]):
    model = WorkSpace
    fields = ('name', 'space_code', 'created_by')
    extra = 0
    can_add_related = False
    can_change_related = False


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'owner', 'created_at')
    readonly_fields = ('id', 'created_at')
    inlines = [WorkspaceInline]


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('user', 'organization', 'role', 'last_activity')
    list_filter = ('role', 'organization')
    readonly_fields = ('id', 'created_at')


@admin.register(OrgInvitation)
class OrgInvitationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('id', 'email', 'sender', 'org_invite', 'created_at', 'accepted')
    list_filter = ('id', 'created_at')
    readonly_fields = ('created_at', 'accepted', 'expired_at')

    @override
    def save_model(
        self, request: HttpRequest, obj: OrgInvitation, form: ModelForm[OrgInvitation], change: bool
    ) -> None:
        try:
            send_invitation_email(obj)
        except InvitationEmailError as exc:
            messages.error(
                request, f'Mailpit rejected the invitation. Status code: {exc.status_code}, Message: {exc.text}'
            )
            messages.set_level(request, messages.ERROR)
            return
        obj.save()


@admin.register(WorkSpace)
class WorkspaceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'space_code', 'organization', 'created_by')
    readonly_fields = ('id', 'created_at')

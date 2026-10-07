from typing import Any, override

import requests
from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest
from requests import HTTPError, RequestException

from conf.settings import EMAIL_HTTP_PORT, EMAIL_SERVICE_HOST, FROM_EMAIL, FRONTED_HOST

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
    list_display = ('id', 'email', 'sender', 'org_invite', 'created_at')
    list_filter = ('id', 'created_at')
    readonly_fields = ('created_at', 'accepted')

    @override
    def save_model(
        self, request: HttpRequest, obj: OrgInvitation, form: ModelForm[OrgInvitation], change: bool
    ) -> None:
        payload: dict[str, Any] = {
        'from': {
                'Email': FROM_EMAIL,
                'Name': FROM_EMAIL,
            },
            'to': [
                {
                    'Email': obj.email.lower(),
                    'Name': obj.email.lower(),
                }
            ],
            'subject': f'Invitation to org {obj.org_invite}',
            'text': str(obj.text_message + '\n' + f'{FRONTED_HOST}/invitation/{obj.id}'),
        }
        try:
            response = requests.post(
                f'http://{EMAIL_SERVICE_HOST}:{EMAIL_HTTP_PORT}/api/v1/send', json=payload, timeout=5
            )
            response.raise_for_status()

            obj.save()
        except HTTPError as exc:
            detail = (
                f'Status code: {exc.response.status_code}, Message: {exc.response.text}'
                if exc.response is not None
                else str(exc)
            )
            messages.error(request, f'Mailpit rejected the invitation. {detail}')
            messages.set_level(request, messages.ERROR)
            return
        except RequestException as exc:
            messages.error(request, f'Mailpit rejected the invitation: {exc}')
            messages.set_level(request, messages.ERROR)
            return


@admin.register(WorkSpace)
class WorkspaceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'space_code', 'organization', 'created_by')
    readonly_fields = ('id', 'created_at')

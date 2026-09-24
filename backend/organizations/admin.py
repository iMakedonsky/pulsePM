import requests
from django.contrib import admin
from django.core.exceptions import BadRequest
from django.forms import ModelForm
from django.http import HttpRequest
from requests.exceptions import Timeout

from conf.settings import EMAIL_HTTP_PORT, EMAIL_SERVICE_HOST, FROM_EMAIL

from .models import Member, Organization, OrgInvitation, WorkSpace


class WorkspaceInline(admin.TabularInline[WorkSpace, Organization]):
    model = WorkSpace
    fields = ('name', 'space_code', 'created_by')
    readonly_fields = ('id',)
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
class OrgInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'sender', 'org_invite', 'accepted', 'created_at')
    list_filter = ('id', 'created_at')
    readonly_fields = ('id', 'created_at')

    def save_model(self, request: HttpRequest, obj: OrgInvitation, form: ModelForm, change) -> None:

        payload = {
            'from': {
                    'Email': FROM_EMAIL,
                    'Name': FROM_EMAIL,
                },
            'to': [
                {
                    'Email': obj.email,
                    'Name': obj.email,
                }
            ],
            'subject': f'Invitation to org {obj.org_invite}',
            'text': str(obj.text_message),
        }
        try:
            response = requests.post(
                f'http://{EMAIL_SERVICE_HOST}:{EMAIL_HTTP_PORT}/api/v1/send', json=payload, timeout=5
            )
            if response.ok:
                obj.save()
            elif response.status_code == requests.codes.bad_request:
                raise BadRequest(response.text)
        except Timeout:
            raise response.reason


# ConnectionError,
#     ConnectTimeout,
#     FileModeWarning,
#     HTTPError,
#     JSONDecodeError,
#     ReadTimeout,
#     RequestException,
#     Timeout,
#     TooManyRedirects,
#     URLRequired,


@admin.register(WorkSpace)
class WorkspaceAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('name', 'space_code', 'organization', 'created_by')
    readonly_fields = ('id', 'created_at')

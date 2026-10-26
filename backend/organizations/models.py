import datetime
import uuid
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.db import models
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja.errors import HttpError

from common.models import BaseModel


def expired_date_at() -> datetime.datetime:
    return timezone.now() + timedelta(minutes=30)


class Organization(BaseModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(max_length=500, null=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Member(BaseModel):
    class OrgRoles(models.TextChoices):
        OWNER = 'owner'
        PM = 'project-manager'
        CONTRIBUTOR = 'contributor'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(choices=OrgRoles.choices, max_length=100, default=OrgRoles.CONTRIBUTOR)
    position = models.CharField(max_length=200, null=True, default='', blank=True)
    location = models.CharField(max_length=200, null=True, default='', blank=True)
    time_zone = models.CharField(max_length=200, null=True, default='', blank=True)
    avatar_url = models.CharField(max_length=200, null=True, default='', blank=True)
    last_activity = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'organization'], name='unique_user_org')]

    def __str__(self) -> str:
        return self.user.email


class OrgInviteManager(models.Manager['OrgInvitation']):
    def get_and_validate_invitation(self, invite_token: str) -> OrgInvitation:
        try:
            decoded_uuid = signing.loads(invite_token, max_age=1800)
            invitation = get_object_or_404(OrgInvitation, pk=decoded_uuid)
            if invitation.accepted is False or invitation.expired_at < timezone.now():
                raise HttpError(410, 'The invitation is no longer valid.')
        except signing.SignatureExpired as exc:
            raise HttpError(410, 'Invitation token has expired!') from exc
        except signing.BadSignature as exc:
            raise HttpError(410, 'Token invalid!') from exc
        except ValueError as exc:
            raise HttpError(400, 'Invalid data') from exc
        except Http404 as exc:
            raise HttpError(404, 'Invitation with that ID does not exist.') from exc
        return invitation

    def all_valid_invitations(self) -> QuerySet[OrgInvitation]:
        return self.get_queryset().filter(expired_at__gt=timezone.now())


class OrgInvitation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    email = models.EmailField(max_length=254, unique=False)
    sender = models.ForeignKey(Member, on_delete=models.CASCADE)
    org_invite = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    text_message = models.TextField(max_length=500, null=False, default='Invitation :)')
    accepted = models.BooleanField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField(default=expired_date_at)

    objects = OrgInviteManager()

    def __str__(self) -> str:
        return str(self.id)


class WorkSpace(BaseModel):
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    space_code = models.CharField(max_length=5, unique=True)
    description = models.TextField(max_length=500, null=True, default='')
    icon_url = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.name

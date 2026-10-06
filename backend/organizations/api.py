import uuid
from typing import cast

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from organizations.schema import (
    InvitationPayload,
    InvitationSchema,
    InvitationUpdateSchema,
    MemberSchema,
    OrganizationPayload,
    OrganizationSchema,
    WorkspaceSchema,
)
from users.models import User

organization_router = Router(tags=['Organizations'])
workspace_router = Router(tags=['Organizations'])
members_router = Router(tags=['Organizations'])
invitation_router = Router(tags=['Invitations'])


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


def assert_membership(request: HttpRequest, org_id: int) -> None:
    """Raise 403 unless the requesting user is a member of the organization."""
    user = cast(AuthenticatedRequest, request).user
    if not Member.objects.filter(user=user.pk, organization=org_id).exists():
        raise HttpError(403, 'Current User is not a member of the Organization.')


@organization_router.post('/create', response={200: OrganizationSchema, 400: dict, 403: dict})
def create_organization(
    request: HttpRequest, payload: OrganizationPayload
) -> Organization | tuple[int, dict[str, str]]:
    user = cast(AuthenticatedRequest, request).user
    try:
        organization = Organization.objects.create(owner_id=user.pk, name=payload.name, description=payload.description)
        Member.objects.create(user=user, organization=organization, role=Member.OrgRoles.OWNER)
    except ValidationError as exc:
        raise HttpError(400, str(exc.message)) from exc
    return organization


@organization_router.get('/{org_id}', response={200: OrganizationSchema, 403: dict, 404: dict})
def get_organization(request: HttpRequest, org_id: int) -> Organization | tuple[int, dict[str, str]]:
    assert_membership(request, org_id)
    try:
        return get_object_or_404(Organization, pk=org_id)
    except Http404 as exc:
        raise HttpError(404, 'Organization with that ID does not exist.') from exc


@workspace_router.get('{org_id}/workspaces', response={200: list[WorkspaceSchema], 403: dict, 404: dict})
def list_workspaces(request: HttpRequest, org_id: int) -> QuerySet[WorkSpace]:
    assert_membership(request, org_id)
    workspaces = WorkSpace.objects.filter(organization=org_id).select_related('organization')
    if not workspaces.exists():
        raise HttpError(404, 'This organization has no workspaces yet.')
    return workspaces


@members_router.get('{org_id}/members', response={200: list[MemberSchema], 403: dict, 404: dict})
def list_members(request: HttpRequest, org_id: int) -> QuerySet[Member]:
    assert_membership(request, org_id)
    members = Member.objects.filter(organization=org_id).select_related('user', 'organization')
    if not members.exists():
        raise HttpError(404, 'This organization has no members yet.')
    return members


@invitation_router.get('/{invitation_id}', response={200: InvitationSchema, 400: dict, 404: dict})
def get_invitation(request: HttpRequest, invitation_id: str) -> OrgInvitation:  # noqa: ARG001
    """Return the invitation for a UUID string, raising 400 if malformed and 404 if absent."""
    try:
        invitation_uuid = uuid.UUID(invitation_id)

        invitation = get_object_or_404(OrgInvitation, pk=invitation_uuid)
    except ValueError as exc:
        raise HttpError(400, 'Invalid data') from exc
    except Http404 as exc:
        raise HttpError(404, 'Invitation with that ID does not exist.') from exc
    return invitation


@invitation_router.patch('/{invitation_id}/accept', response={200: InvitationUpdateSchema, 400: dict, 404: dict})
def update_invitation(
    request: HttpRequest, invitation_id: str, payload: InvitationPayload
) -> dict[str, bool | Member | None]:
    invitation = get_invitation(request, invitation_id)
    if not payload.accepted:
        invitation.accepted = False
        invitation.save()
        return {'accepted': invitation.accepted, 'member': None}
    try:
        user = get_object_or_404(User, email__iexact=invitation.email)
    except Http404 as exc:
        raise HttpError(404, 'User with the invitation email is not registered.') from exc

    member, _ = Member.objects.get_or_create(user=user, organization=invitation.org_invite)
    invitation.accepted = True
    invitation.save()
    return {'accepted': invitation.accepted, 'member': member}

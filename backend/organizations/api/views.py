from collections.abc import Callable
from functools import wraps
from typing import Concatenate, cast

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router, Status
from ninja.errors import HttpError

from organizations.api.schemas import (
    InvalidOrganizationIdError,
    InvitationListNotFoundError,
    InvitationListResponse,
    MemberSchema,
    MembersNotFoundError,
    OrganizationBadRequestError,
    OrganizationConflictError,
    OrganizationForbiddenError,
    OrganizationNotFoundError,
    OrganizationPayload,
    OrganizationSchema,
    OrganizationUpdatePayload,
)
from organizations.models import Member, Organization, OrgInvitation
from users.models import User

organization_router = Router(tags=['Organizations'])
members_router = Router(tags=['Organizations'])


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


def assert_membership[**P, T](
    endpoint: Callable[Concatenate[HttpRequest, int, P], T],
) -> Callable[Concatenate[HttpRequest, int, P], T]:
    """Raise 403 unless the requesting user is a member of the `org_id` organization."""

    @wraps(endpoint)
    def inner_assert_membership(request: HttpRequest, org_id: int, *args: P.args, **kwargs: P.kwargs) -> T:
        user = cast(AuthenticatedRequest, request).user
        if not Member.objects.filter(user=user.pk, organization=org_id).exists():
            raise HttpError(403, 'Current User is not a member of the Organization.')
        return endpoint(request, org_id, *args, **kwargs)

    return cast(Callable[Concatenate[HttpRequest, int, P], T], inner_assert_membership)


def get_organization(org_id: int) -> Organization:
    """Return the organization, otherwise raise 404."""
    try:
        return get_object_or_404(Organization, pk=org_id)
    except Http404 as exc:
        raise HttpError(404, 'Organization with that ID does not exist.') from exc


@organization_router.post(
    '/create',
    response={201: OrganizationSchema, 400: OrganizationBadRequestError, 409: OrganizationConflictError},
)
def create_organization(request: HttpRequest, payload: OrganizationPayload) -> Status[Organization]:
    user = cast(AuthenticatedRequest, request).user
    if Organization.objects.filter(owner=user.pk).exists():
        raise HttpError(409, 'User already owns an organization.')
    try:
        organization = Organization.objects.create(owner_id=user.pk, name=payload.name, description=payload.description)
        Member.objects.create(user=user, organization=organization, role=Member.OrgRoles.OWNER)
    except ValidationError as exc:
        raise HttpError(400, '; '.join(exc.messages)) from exc
    return Status(201, organization)


@organization_router.get(
    '/{org_id}',
    response={
        200: OrganizationSchema,
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: OrganizationNotFoundError,
    },
)
@assert_membership
def get_organization_detail(request: HttpRequest, org_id: int) -> Organization:  # noqa: ARG001
    return get_organization(org_id)


@organization_router.patch(
    '/{org_id}/update',
    response={
        200: OrganizationSchema,
        400: OrganizationBadRequestError,
        403: OrganizationForbiddenError,
        404: OrganizationNotFoundError,
    },
)
@assert_membership
def update_organization(request: HttpRequest, org_id: int, payload: OrganizationUpdatePayload) -> Organization:  # noqa: ARG001
    organization = get_organization(org_id)
    changes = payload.dict(exclude_unset=True)
    for field, value in changes.items():
        setattr(organization, field, value)
    try:
        organization.save()
    except ValidationError as exp:
        raise HttpError(400, ', '.join(exp.messages)) from exp
    return organization


@organization_router.delete(
    '/{org_id}/delete',
    response={
        200: None,
        403: OrganizationForbiddenError,
        404: OrganizationNotFoundError,
    },
)
@assert_membership
def delete_organization(request: HttpRequest, org_id: int) -> tuple[int, None]:  # noqa: ARG001
    organization = get_organization(org_id)
    organization.delete()
    return 200, None


@members_router.get(
    '{org_id}/members',
    response={
        200: list[MemberSchema],
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: MembersNotFoundError,
    },
)
@assert_membership
def list_members(request: HttpRequest, org_id: int) -> QuerySet[Member]:  # noqa: ARG001
    members = Member.objects.filter(organization=org_id).select_related('user', 'organization')
    if not members.exists():
        raise HttpError(404, 'This organization has no members yet.')
    return members


@members_router.get(
    '{org_id}/invitations',
    response={
        200: list[InvitationListResponse],
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: InvitationListNotFoundError,
    },
)
@assert_membership
def list_invitations(request: HttpRequest, org_id: int) -> QuerySet[OrgInvitation]:  # noqa: ARG001
    invitations = OrgInvitation.objects.filter(org_invite=org_id).order_by('-created_at')
    if not invitations.exists():
        raise HttpError(404, 'This organization has no invitations yet.')
    return invitations

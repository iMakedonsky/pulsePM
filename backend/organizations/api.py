from typing import cast

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from organizations.models import Member, Organization
from organizations.schema import (
    InvalidOrganizationIdError,
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
from users.models import User

organization_router = Router(tags=['Organizations'])
members_router = Router(tags=['Organizations'])


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


def assert_membership(request: HttpRequest, org_id: int) -> Member:
    """Return the requesting user's Member in the organization, or raise 403 if they are not a member."""
    user = cast(AuthenticatedRequest, request).user
    member = Member.objects.filter(user=user.pk, organization=org_id).first()
    if member is None:
        raise HttpError(403, 'Current User is not a member of the Organization.')
    return member


def get_organization(org_id: int) -> Organization:
    """Return the organization, otherwise raise 404."""
    try:
        return get_object_or_404(Organization, pk=org_id)
    except Http404 as exc:
        raise HttpError(404, 'Organization with that ID does not exist.') from exc


def save_organization(organization: Organization) -> None:
    """Save the organization (the model validates on save); report validation failures as 400."""
    try:
        organization.save()
    except ValidationError as exc:
        raise HttpError(400, '; '.join(exc.messages)) from exc


@organization_router.post(
    '/create',
    response={200: OrganizationSchema, 400: OrganizationBadRequestError, 409: OrganizationConflictError},
)
def create_organization(request: HttpRequest, payload: OrganizationPayload) -> Organization:
    user = cast(AuthenticatedRequest, request).user
    if Organization.objects.filter(owner=user.pk).exists():
        raise HttpError(409, 'User already owns an organization.')
    try:
        organization = Organization.objects.create(owner_id=user.pk, name=payload.name, description=payload.description)
        Member.objects.create(user=user, organization=organization, role=Member.OrgRoles.OWNER)
    except ValidationError as exc:
        raise HttpError(400, '; '.join(exc.messages)) from exc
    return organization


@organization_router.get(
    '/{org_id}',
    response={
        200: OrganizationSchema,
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: OrganizationNotFoundError,
    },
)
def get_organization_detail(request: HttpRequest, org_id: int) -> Organization:
    assert_membership(request, org_id)
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
def update_organization(request: HttpRequest, org_id: int, payload: OrganizationUpdatePayload) -> Organization:
    assert_membership(request, org_id)
    organization = get_organization(org_id)
    changes = payload.dict(exclude_unset=True)
    for field, value in changes.items():
        setattr(organization, field, value)
    save_organization(organization)
    return organization


@organization_router.delete(
    '/{org_id}/delete',
    response={
        200: None,
        403: OrganizationForbiddenError,
        404: OrganizationNotFoundError,
    },
)
def delete_organization(request: HttpRequest, org_id: int) -> tuple[int, None]:
    assert_membership(request, org_id)
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
def list_members(request: HttpRequest, org_id: int) -> QuerySet[Member]:
    assert_membership(request, org_id)
    members = Member.objects.filter(organization=org_id).select_related('user', 'organization')
    if not members.exists():
        raise HttpError(404, 'This organization has no members yet.')
    return members

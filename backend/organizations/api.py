from collections.abc import Callable
from functools import wraps
from typing import cast

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from organizations.models import Member, Organization, WorkSpace
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
    WorkspaceSchema,
    WorkspacesNotFoundError,
)
from users.models import User

organization_router = Router(tags=['Organizations'])
workspace_router = Router(tags=['Workspaces'])
members_router = Router(tags=['Members'])


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


def assert_membership[T](endpoint: Callable[[HttpRequest, int], T]) -> Callable[[HttpRequest, int], T]:
    @wraps(endpoint)
    def inner_assert_membership(request: HttpRequest, org_id: int) -> T:
        user = cast(AuthenticatedRequest, request).user
        if not Member.objects.filter(user=user.pk, organization=org_id).exists():
            raise HttpError(403, 'Current User is not a member of the Organization.')
        return endpoint(request, org_id)

    return inner_assert_membership


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
@assert_membership
def get_organization(request: HttpRequest, org_id: int) -> Organization:  # noqa: ARG001
    try:
        return get_object_or_404(Organization, pk=org_id)
    except Http404 as exc:
        raise HttpError(404, 'Organization with that ID does not exist.') from exc


@workspace_router.get(
    '{org_id}/workspaces',
    response={
        200: list[WorkspaceSchema],
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: WorkspacesNotFoundError,
    },
)
@assert_membership
def list_workspaces(request: HttpRequest, org_id: int) -> QuerySet[WorkSpace]:  # noqa: ARG001
    workspaces = WorkSpace.objects.filter(organization=org_id).select_related('organization')
    if not workspaces.exists():
        raise HttpError(404, 'This organization has no workspaces yet.')
    return workspaces


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

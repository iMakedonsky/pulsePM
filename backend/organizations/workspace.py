from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from organizations.api import assert_membership
from organizations.models import WorkSpace
from organizations.schema import (
    InvalidOrganizationIdError,
    OrganizationForbiddenError,
    WorkspaceBadRequestError,
    WorkspaceCreatePayload,
    WorkspaceNotFoundError,
    WorkspaceSchema,
    WorkspacesNotFoundError,
    WorkspaceUpdatePayload,
)

workspace_router = Router(tags=['Workspaces'])


def get_workspace(org_id: int, workspace_id: int) -> WorkSpace:
    """Return the workspace if it belongs to the organization, otherwise raise 404."""
    try:
        return get_object_or_404(WorkSpace, pk=workspace_id, organization=org_id)
    except Http404 as exc:
        raise HttpError(404, 'Workspace with that ID does not exist.') from exc


def save_workspace(workspace: WorkSpace) -> None:
    """Validate and save the workspace; the model has no clean-on-save, so report failures as 400."""
    try:
        workspace.full_clean()
        workspace.save()
    except ValidationError as exc:
        raise HttpError(400, '; '.join(exc.messages)) from exc


@workspace_router.post(
    '{org_id}/workspaces/create',
    response={
        200: WorkspaceSchema,
        400: WorkspaceBadRequestError,
        403: OrganizationForbiddenError,
    },
)
def create_workspace(request: HttpRequest, org_id: int, payload: WorkspaceCreatePayload) -> WorkSpace:
    creator = assert_membership(request, org_id)
    workspace = WorkSpace(organization_id=org_id, created_by=creator, **payload.dict(exclude_unset=True))
    save_workspace(workspace)
    return workspace


@workspace_router.get(
    '{org_id}/workspaces',
    response={
        200: list[WorkspaceSchema],
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: WorkspacesNotFoundError,
    },
)
def list_workspaces(request: HttpRequest, org_id: int) -> QuerySet[WorkSpace]:
    assert_membership(request, org_id)
    workspaces = WorkSpace.objects.filter(organization=org_id).select_related('organization')
    if not workspaces.exists():
        raise HttpError(404, 'This organization has no workspaces yet.')
    return workspaces


@workspace_router.get(
    '{org_id}/workspaces/{workspace_id}',
    response={
        200: WorkspaceSchema,
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: WorkspaceNotFoundError,
    },
)
def get_workspace_detail(request: HttpRequest, org_id: int, workspace_id: int) -> WorkSpace:
    assert_membership(request, org_id)
    return get_workspace(org_id, workspace_id)


@workspace_router.patch(
    '{org_id}/workspaces/{workspace_id}/update',
    response={
        200: WorkspaceSchema,
        400: WorkspaceBadRequestError,
        403: OrganizationForbiddenError,
        404: WorkspaceNotFoundError,
    },
)
def update_workspace(
    request: HttpRequest, org_id: int, workspace_id: int, payload: WorkspaceUpdatePayload
) -> WorkSpace:
    assert_membership(request, org_id)
    workspace = get_workspace(org_id, workspace_id)
    changes = payload.dict(exclude_unset=True)
    for field, value in changes.items():
        setattr(workspace, field, value)
    save_workspace(workspace)
    return workspace


@workspace_router.delete(
    '{org_id}/workspaces/{workspace_id}/delete',
    response={
        200: None,
        403: OrganizationForbiddenError,
        404: WorkspaceNotFoundError,
    },
)
def delete_workspace(request: HttpRequest, org_id: int, workspace_id: int) -> tuple[int, None]:
    assert_membership(request, org_id)
    get_workspace(org_id, workspace_id).delete()
    return 200, None

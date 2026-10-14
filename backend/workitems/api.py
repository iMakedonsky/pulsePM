from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from organizations.api import assert_membership
from organizations.models import Member, WorkSpace
from organizations.schema import InvalidOrganizationIdError, OrganizationForbiddenError
from workitems.models import WorkItem
from workitems.schema import (
    WorkItemBadRequestError,
    WorkItemCreatePayload,
    WorkItemNotFoundError,
    WorkItemSchema,
    WorkItemUpdatePayload,
)

workitem_router = Router(tags=['Work items'])


def organization_workitems(org_id: int) -> QuerySet[WorkItem]:
    """Work items that belong to the organization."""
    return WorkItem.objects.filter(organization=org_id)


def get_workitem(org_id: int, workitem_id: int) -> WorkItem:
    """Return the work item if it belongs to the organization, otherwise raise 404."""
    try:
        return get_object_or_404(organization_workitems(org_id), pk=workitem_id)
    except Http404 as exc:
        raise HttpError(404, 'Work item with that ID does not exist.') from exc


def check_references(org_id: int, changes: dict[str, Any]) -> None:
    """Reject an assignee or workspace that lies outside the organization."""
    assignee = changes.get('assigned_to')
    if assignee is not None and not Member.objects.filter(pk=assignee, organization=org_id).exists():
        raise HttpError(400, 'Assignee is not a member of this organization.')
    workspace = changes.get('workspace')
    if workspace is not None and not WorkSpace.objects.filter(pk=workspace, organization=org_id).exists():
        raise HttpError(400, 'Workspace does not belong to this organization.')


def to_model_fields(changes: dict[str, Any]) -> dict[str, Any]:
    """Map payload keys to model attributes: foreign keys are set by id."""
    return {f'{key}_id' if key in {'assigned_to', 'workspace'} else key: value for key, value in changes.items()}


def save_workitem(workitem: WorkItem) -> None:
    """Validate and save the work item; report validation failures as 400."""
    try:
        workitem.save()
    except ValidationError as exc:
        raise HttpError(400, '; '.join(exc.messages)) from exc


@workitem_router.post(
    '{org_id}/workitems/create',
    response={
        200: WorkItemSchema,
        400: WorkItemBadRequestError,
        403: OrganizationForbiddenError,
    },
)
def create_workitem(request: HttpRequest, org_id: int, payload: WorkItemCreatePayload) -> WorkItem:
    creator = assert_membership(request, org_id)
    changes = payload.dict(exclude_unset=True)
    check_references(org_id, changes)
    workitem = WorkItem(organization_id=org_id, created_by=creator, **to_model_fields(changes))
    save_workitem(workitem)
    return workitem


@workitem_router.get(
    '{org_id}/workitems',
    response={
        200: list[WorkItemSchema],
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
    },
)
def list_workitems(request: HttpRequest, org_id: int) -> QuerySet[WorkItem]:
    assert_membership(request, org_id)
    return organization_workitems(org_id)


@workitem_router.get(
    '{org_id}/workitems/{workitem_id}',
    response={
        200: WorkItemSchema,
        400: InvalidOrganizationIdError,
        403: OrganizationForbiddenError,
        404: WorkItemNotFoundError,
    },
)
def get_workitem_detail(request: HttpRequest, org_id: int, workitem_id: int) -> WorkItem:
    assert_membership(request, org_id)
    return get_workitem(org_id, workitem_id)


@workitem_router.patch(
    '{org_id}/workitems/{workitem_id}/update',
    response={
        200: WorkItemSchema,
        400: WorkItemBadRequestError,
        403: OrganizationForbiddenError,
        404: WorkItemNotFoundError,
    },
)
def update_workitem(request: HttpRequest, org_id: int, workitem_id: int, payload: WorkItemUpdatePayload) -> WorkItem:
    assert_membership(request, org_id)
    workitem = get_workitem(org_id, workitem_id)
    changes = payload.dict(exclude_unset=True)
    check_references(org_id, changes)
    for field, value in to_model_fields(changes).items():
        setattr(workitem, field, value)
    workitem.last_update = timezone.now()
    save_workitem(workitem)
    return workitem


@workitem_router.delete(
    '{org_id}/workitems/{workitem_id}/delete',
    response={
        200: None,
        403: OrganizationForbiddenError,
        404: WorkItemNotFoundError,
    },
)
def delete_workitem(request: HttpRequest, org_id: int, workitem_id: int) -> tuple[int, None]:
    assert_membership(request, org_id)
    get_workitem(org_id, workitem_id).delete()
    return 200, None

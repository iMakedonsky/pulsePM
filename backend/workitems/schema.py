from datetime import date, datetime

from ninja import ModelSchema, Schema
from pydantic import Field

from users.schema import ErrorSchema
from workitems.models import WorkItem


class WorkItemSchema(ModelSchema):
    class Meta:
        model = WorkItem
        fields = [
            'id',
            'organization',
            'workspace',
            'created_by',
            'assigned_to',
            'title',
            'description',
            'status',
            'priority',
            'created_at',
            'started_at',
            'due_date',
            'estimated_time',
            'time_spent',
            'last_update',
        ]


class WorkItemCreatePayload(Schema):
    """`workspace` is optional: a work item may live in the organization without belonging to a workspace."""

    title: str
    assigned_to: int
    due_date: date
    workspace: int | None = None
    description: str | None = None
    status: WorkItem.Status | None = None
    priority: WorkItem.Priority | None = None
    started_at: datetime | None = None
    estimated_time: int | None = None
    time_spent: int | None = None


class WorkItemUpdatePayload(Schema):
    """Only the fields that are sent change; send `workspace: null` to detach the item from its workspace."""

    title: str | None = None
    assigned_to: int | None = None
    due_date: date | None = None
    workspace: int | None = None
    description: str | None = None
    status: WorkItem.Status | None = None
    priority: WorkItem.Priority | None = None
    started_at: datetime | None = None
    estimated_time: int | None = None
    time_spent: int | None = None


class WorkItemBadRequestError(ErrorSchema):
    detail: str = Field(
        examples=[
            'This field cannot be blank.',
            'Value cannot be in the past.',
            'Assignee is not a member of this organization.',
            'Workspace does not belong to this organization.',
        ]
    )


class WorkItemNotFoundError(ErrorSchema):
    detail: str = Field(examples=['Work item with that ID does not exist.'])

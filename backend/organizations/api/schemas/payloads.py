from ninja import Schema
from pydantic import EmailStr, Field


class OrganizationPayload(Schema):
    name: str
    description: str


class OrganizationUpdatePayload(Schema):
    name: str | None = None
    description: str | None = None


class InvitationPayload(Schema):
    accepted: bool


class InvitationCreatePayload(Schema):
    email: EmailStr
    text_message: str = Field(default='Invitation :)', max_length=500)


class WorkspaceCreatePayload(Schema):
    name: str
    space_code: str
    icon_url: str
    description: str | None = None


class WorkspaceUpdatePayload(Schema):
    name: str | None = None
    icon_url: str | None = None
    description: str | None = None

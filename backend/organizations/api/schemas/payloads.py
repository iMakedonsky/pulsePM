from ninja import Schema
from pydantic import EmailStr, Field


class OrganizationPayload(Schema):
    name: str
    description: str


class InvitationPayload(Schema):
    accepted: bool


class InvitationCreatePayload(Schema):
    email: EmailStr
    text_message: str = Field(default='Invitation :)', max_length=500)

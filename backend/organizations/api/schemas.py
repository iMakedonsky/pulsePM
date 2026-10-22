from typing import TypedDict

from ninja import ModelSchema, Schema
from pydantic import Field

from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from users.api.schemas import ErrorSchema
from users.models import User


class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'owner', 'name', 'description']


class OrganizationPayload(Schema):
    name: str
    description: str


class UserBrief(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class MemberSchema(ModelSchema):
    user: UserBrief

    class Meta:
        model = Member
        fields = ['id', 'organization', 'role']


class WorkspaceSchema(ModelSchema):
    class Meta:
        model = WorkSpace
        fields = ['id', 'name', 'space_code', 'created_by']


class InvitationResponse(ModelSchema):
    class Meta:
        model = OrgInvitation
        fields = ['org_invite', 'accepted', 'email', 'text_message']


class InvitationResult(TypedDict):
    """What `get_invitation` returns in Python: the live model, not its serialised schema."""

    invitation: OrgInvitation


class InvitationUpdateResult(TypedDict):
    """What `update_invitation` returns in Python: the live member model, not its serialised schema."""

    accepted: bool
    member: Member | None


class InvitationPayload(Schema):
    accepted: bool


class InvitationUpdateSchema(Schema):
    accepted: bool
    member: MemberSchema | None = None


class OrganizationBadRequestError(ErrorSchema):
    detail: str = Field(
        examples=[
            'This field cannot be blank.',
            'Ensure this value has at most 100 characters (it has 101).',
        ]
    )


class InvalidOrganizationIdError(ErrorSchema):
    detail: str = Field(examples=['Invalid org_id.'])


class OrganizationForbiddenError(ErrorSchema):
    detail: str = Field(examples=['Current User is not a member of the Organization.'])


class OrganizationNotFoundError(ErrorSchema):
    detail: str = Field(examples=['Organization with that ID does not exist.'])


class WorkspacesNotFoundError(ErrorSchema):
    detail: str = Field(examples=['This organization has no workspaces yet.'])


class MembersNotFoundError(ErrorSchema):
    detail: str = Field(examples=['This organization has no members yet.'])


class OrganizationConflictError(ErrorSchema):
    detail: str = Field(examples=['User already owns an organization.'])


class InvitationBadRequestError(ErrorSchema):
    detail: str = Field(examples=['Invalid data'])


class InvitationNotFoundError(ErrorSchema):
    detail: str = Field(examples=['Invitation with that ID does not exist.'])


class InvitationGoneError(ErrorSchema):
    detail: str = Field(examples=['Token invalid!', 'Invitation token has expired!'])


class InvitationUpdateNotFoundError(ErrorSchema):
    detail: str = Field(examples=['Invitation with that ID does not exist.', 'User with that email does not exist.'])


class InvitationConflictError(ErrorSchema):
    detail: str = Field(examples=['The user ada@example.com is already invited to organization Acme.'])


class InvitationUpdateGoneError(ErrorSchema):
    detail: str = Field(examples=['Token invalid!', 'Invitation token has expired!'])

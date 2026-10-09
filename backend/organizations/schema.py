from typing import TypedDict

from ninja import ModelSchema, Schema
from pydantic import Field

from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from users.models import User
from users.schema import ErrorSchema


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


class InvitationSchema(ModelSchema):
    class Meta:
        model = OrgInvitation
        fields = ['org_invite', 'accepted', 'email', 'text_message']


class InvitationResponse(Schema):
    invitation: InvitationSchema
    invitation_token: str


class InvitationResult(TypedDict):
    """What `get_invitation` returns in Python: the live model, not its serialised schema."""

    invitation: OrgInvitation
    invitation_token: str


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
    detail: str = Field(examples=['Name: This field cannot be blank.'])


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

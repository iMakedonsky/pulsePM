from typing import TypedDict

from ninja import ModelSchema, Schema

from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from users.models import User


class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'owner', 'name', 'description']


class OrganizationPayload(Schema):
    user_id: int
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


class InvitationPayload(Schema):
    accepted: bool


class InvitationUpdateSchema(Schema):
    accepted: bool
    member: MemberSchema | None = None

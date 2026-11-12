from typing import Annotated, TypedDict

from ninja import Field, ModelSchema, Schema

from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from users.models import User


class OrganizationSchema(ModelSchema):
    owner_name: Annotated[str, Field(alias='owner.email')]

    class Meta:
        model = Organization
        fields = ['id', 'owner', 'name', 'description']


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
    creator_name: str

    class Meta:
        model = WorkSpace
        fields = ['id', 'name', 'space_code', 'created_by']


class InvitationResponse(ModelSchema):
    org_name: str

    class Meta:
        model = OrgInvitation
        fields = ['org_invite', 'accepted', 'email', 'expired_at']


class InvitationListResponse(ModelSchema):
    sender_name: str

    class Meta:
        model = OrgInvitation
        fields = ['id', 'org_invite', 'accepted', 'email', 'text_message', 'created_at', 'expired_at']


class InvitationUpdateSchema(Schema):
    accepted: bool
    member: MemberSchema | None = None


class InvitationResult(TypedDict):
    """What `get_invitation` returns in Python: the live model, not its serialised schema."""

    invitation: OrgInvitation


class InvitationUpdateResult(TypedDict):
    """What `update_invitation` returns in Python: the live member model, not its serialised schema."""

    accepted: bool
    member: Member | None

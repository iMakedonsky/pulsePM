from typing import TypedDict

from ninja import ModelSchema, Schema

from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from users.models import User


class OrganizationSchema(ModelSchema):
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
    class Meta:
        model = WorkSpace
        fields = ['id', 'name', 'space_code', 'created_by']


class InvitationResponse(ModelSchema):
    # org_name: Annotated[str, Field(alias="org_invite.org_name")] noqa: ERA001
    org_name: str

    class Meta:
        model = OrgInvitation
        fields = ['org_invite', 'accepted', 'email', 'text_message', 'expired_at']


class InvitationListResponse(ModelSchema):
    class Meta:
        model = OrgInvitation
        fields = ['id', 'org_invite', 'accepted', 'email', 'sender', 'text_message', 'created_at', 'expired_at']


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

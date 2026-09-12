from ninja import ModelSchema, Schema

from organizations.models import Member, Organization, WorkSpace
from users.models import User


class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'owner', 'name', 'description']


class OrganizationPayload(Schema):
    owner_id: int
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

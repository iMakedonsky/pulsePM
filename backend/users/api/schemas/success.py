from ninja import ModelSchema

from organizations.models import Member, Organization
from users.models import User


class UserProfileSchema(ModelSchema):
    """Full profile view; extend when a profile-update endpoint is added."""

    avatar_url: str = ''

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class UserResponse(ModelSchema):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class OrganizationBrief(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'name']


class GetListParticipation(ModelSchema):
    organization: OrganizationBrief

    class Meta:
        model = Member
        fields = ['id', 'role', 'position', 'last_activity']

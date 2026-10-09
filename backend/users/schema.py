from ninja import ModelSchema, Schema
from pydantic import EmailStr, Field

from organizations.models import Member, Organization
from users.models import User


class UserProfileSchema(ModelSchema):
    """Full profile view; extend when a profile-update endpoint is added."""

    avatar_url: str = ''

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class RegisterPayload(Schema):
    email: EmailStr
    password: str


class LoginPayload(Schema):
    email: str
    password: str


class ErrorSchema(Schema):
    """Body of any `HttpError`: ninja serialises it as `{'detail': message}`."""

    detail: str


class BadRequestError(ErrorSchema):
    detail: str = Field(
        examples=[
            'Provided password is invalid; Registration email does not match the invitation; Invalid data',
        ]
    )


class UnauthorizedError(ErrorSchema):
    detail: str = Field(examples=['Invalid email or password.'])


class NotFoundError(ErrorSchema):
    detail: str = Field(
        examples=[
            'Invitation with that ID does not exist; User with that email does not exist.',
        ]
    )


class ConflictError(ErrorSchema):
    detail: str = Field(examples=['User already exists with the same email.'])


class GoneError(ErrorSchema):
    detail: str = Field(examples=['Invitation expired!', 'Token expired!', 'Invitation token has expired!'])


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

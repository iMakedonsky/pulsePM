from ninja import Schema
from pydantic import Field


class ErrorSchema(Schema):
    """Body of any `HttpError`: ninja serialises it as `{'detail': message}`."""

    detail: str


class BadRequestError(ErrorSchema):
    detail: str = Field(
        examples=[
            'Provided password is invalid.',
            'Registration email does not match the invitation.',
            'Invalid data',
        ]
    )


class UnauthorizedError(ErrorSchema):
    detail: str = Field(examples=['Invalid email or password.'])


class NotFoundError(ErrorSchema):
    detail: str = Field(
        examples=[
            'Invitation with that ID does not exist.',
            (
                'User with email "ada@example.com" does not exist. '
                'First create own account then login in and try to accept again!'
            ),
        ]
    )


class ConflictError(ErrorSchema):
    detail: str = Field(examples=['User already exists with the same email.'])


class GoneError(ErrorSchema):
    detail: str = Field(
        examples=['Token invalid!', 'Invitation token has expired!', 'The invitation is no longer valid.']
    )


class SessionUnauthorizedError(ErrorSchema):
    detail: str = Field(examples=['Unauthorized'])


class MembershipNotFoundError(ErrorSchema):
    detail: str = Field(examples=["User haven't participated yet."])

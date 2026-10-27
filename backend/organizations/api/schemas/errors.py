from pydantic import Field

from users.api.schemas.errors import ErrorSchema


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
    detail: str = Field(
        examples=['Token invalid!', 'Invitation token has expired!', 'The invitation is no longer valid.']
    )


class InvitationListNotFoundError(ErrorSchema):
    detail: str = Field(examples=['The organization has no invitations yet.'])


class InvitationUpdateNotFoundError(ErrorSchema):
    detail: str = Field(
        examples=[
            'Invitation with that ID does not exist.',
            (
                'User with email "ada@example.com" does not exist. '
                'First create own account then login in and try to accept again!'
            ),
        ]
    )


class InvitationConflictError(ErrorSchema):
    detail: str = Field(examples=['The user ada@example.com is already invited to organization Acme.'])


class InvitationUpdateGoneError(ErrorSchema):
    detail: str = Field(
        examples=['Token invalid!', 'Invitation token has expired!', 'The invitation is no longer valid.']
    )

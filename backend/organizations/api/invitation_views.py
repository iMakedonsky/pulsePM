from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from organizations.api.schemas import (
    InvitationBadRequestError,
    InvitationConflictError,
    InvitationGoneError,
    InvitationNotFoundError,
    InvitationPayload,
    InvitationResponse,
    InvitationResult,
    InvitationUpdateGoneError,
    InvitationUpdateNotFoundError,
    InvitationUpdateResult,
    InvitationUpdateSchema,
)
from organizations.models import Member, OrgInvitation
from users.models import User

invitation_router = Router(tags=['Temporary Invitations'])


@invitation_router.get(
    '/{invite_token}',
    response={
        200: InvitationResponse,
        400: InvitationBadRequestError,
        404: InvitationNotFoundError,
        410: InvitationGoneError,
    },
)
def get_invitation(request: HttpRequest, invite_token: str) -> InvitationResult:  # noqa: ARG001
    return InvitationResult(
        invitation=OrgInvitation.objects.get_and_validate_invitation(invite_token), invitation_token=invite_token
    )


@invitation_router.patch(
    '/{invite_token}/accept',
    response={
        200: InvitationUpdateSchema,
        400: InvitationBadRequestError,
        404: InvitationUpdateNotFoundError,
        409: InvitationConflictError,
        410: InvitationUpdateGoneError,
    },
)
def accept_invitation(
    request: HttpRequest,  # noqa: ARG001
    payload: InvitationPayload,
    invite_token: str,
) -> InvitationUpdateResult:
    invitation = OrgInvitation.objects.get_and_validate_invitation(invite_token)
    if not payload.accepted:
        invitation.accepted = False
        invitation.save()
        return {'accepted': invitation.accepted, 'member': None}

    user = User.objects.filter(email__iexact=invitation.email).first()
    if not user:
        raise HttpError(404, 'User with that email does not exist.')

    member, created_bool = Member.objects.get_or_create(user=user, organization=invitation.org_invite)
    if not created_bool:
        raise HttpError(409, f'The user {user} is already invited to organization {invitation.org_invite}.')

    invitation.accepted = True
    invitation.save()
    return {'accepted': invitation.accepted, 'member': member}

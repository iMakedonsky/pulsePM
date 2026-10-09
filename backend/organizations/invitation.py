from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from organizations.models import Member, OrgInvitation
from organizations.schema import (
    InvitationPayload,
    InvitationResponse,
    InvitationResult,
    InvitationUpdateResult,
    InvitationUpdateSchema,
)
from users.models import User

invitation_router = Router(tags=['Temporary Invitations'])


@invitation_router.get('/{invite_token}', response={200: InvitationResponse, 400: dict, 404: dict, 410: dict})
def get_invitation(request: HttpRequest, invite_token: str) -> InvitationResult:  # noqa: ARG001
    """Return the invitation for a signed token.

    Raises 400 if malformed, 404 if absent and 410 if the invitation is expired.
    """
    try:
        decoded_uuid = signing.loads(invite_token)

        invitation = get_object_or_404(OrgInvitation, pk=decoded_uuid)

        if invitation.expired_at <= timezone.now() or invitation.accepted is False:
            raise HttpError(410, 'Invitation expired!')
    except BadSignature as exc:
        raise HttpError(410, 'Token expired!') from exc
    except ValueError as exc:
        raise HttpError(400, 'Invalid data') from exc
    except Http404 as exc:
        raise HttpError(404, 'Invitation with that ID does not exist.') from exc
    return {'invitation': invitation, 'invitation_token': invite_token}


@invitation_router.patch(
    '/{invite_token}/accept',
    response={200: InvitationUpdateSchema, 400: dict, 404: dict, 409: dict, 410: dict},
)
def update_invitation(
    request: HttpRequest,
    payload: InvitationPayload,
    invite_token: str,
) -> InvitationUpdateResult:
    invitation = get_invitation(request, invite_token)['invitation']
    if not payload.accepted:
        invitation.accepted = False
        invitation.save()
        return {'accepted': invitation.accepted, 'member': None}

    user = User.objects.filter(email__iexact=invitation.email).first()
    if not user:
        raise HttpError(404, 'User with that email does not exist.')

    try:
        signing.loads(invite_token, max_age=1800)

    except SignatureExpired as exc:
        raise HttpError(410, 'Invitation token has expired!') from exc

    member, created_bool = Member.objects.get_or_create(user=user, organization=invitation.org_invite)
    if not created_bool:
        raise HttpError(409, f'The user {user} is already invited to organization {invitation.org_invite}.')

    invitation.accepted = True
    invitation.save()
    return {'accepted': invitation.accepted, 'member': member}

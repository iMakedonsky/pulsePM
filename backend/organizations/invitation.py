import uuid

from django.core.signing import TimestampSigner, SignatureExpired
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from organizations.models import Member, OrgInvitation
from organizations.schema import (
    InvitationPayload,
    InvitationSchema,
    InvitationUpdateSchema,
)
from users.models import User

invitation_router = Router(tags=['Invitations'])

def get_token(value: str, operation) -> str:
    signer = TimestampSigner()
    signing_key = value
    if operation == 'enc':
        signing_key = signer.sign(value)
    elif operation == 'dec':
        signing_key = signer.unsign(value)
    return signing_key

@invitation_router.get('/{invitation_id}', response={200: InvitationSchema, 400: dict, 404: dict})
def get_invitation(request: HttpRequest, invitation_id: str) -> OrgInvitation:  # noqa: ARG001
    """Return the invitation for a UUID string, raising 400 if malformed and 404 if absent."""
    try:
        invitation_uuid = uuid.UUID(invitation_id)

        invitation = get_object_or_404(OrgInvitation, pk=invitation_uuid)
    except ValueError as exc:
        raise HttpError(400, 'Invalid data') from exc
    except Http404 as exc:
        raise HttpError(404, 'Invitation with that ID does not exist.') from exc
    return invitation

@invitation_router.patch('/{invitation_id}/accept', response={200: InvitationUpdateSchema, 302: dict, 400: dict, 404: dict})
def update_invitation(
    request: HttpRequest, invitation_id: str, payload: InvitationPayload, token: str | None
) -> dict[str, bool | Member | None]:
    invitation = get_invitation(request, invitation_id)
    if not payload.accepted:
        invitation.accepted = False
        invitation.save()
        return {'accepted': invitation.accepted, 'member': None}

    user = User.objects.filter(email__iexact=invitation.email).first()
    if not user:
        signer = TimestampSigner()
        token = signer.sign(invitation.email)

        return {'Redirect': HttpResponseRedirect, 'token': token}

    if token:
        try:
            signer = TimestampSigner()
            signer.unsign(token, max_age=20)

        except SignatureExpired as exc:
            raise HttpError(410, 'Invitation token was gone') from exc

        member, _ = Member.objects.get_or_create(user=user, organization=invitation.org_invite)
        invitation.accepted = True
        invitation.save()
        return {'accepted': invitation.accepted, 'member': member}
    else:
        raise HttpError(400, 'Token is missing') from None

# TODO: consider how to implement timestamp to invitation link (via date verify).
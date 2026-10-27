from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest
from ninja import Router, Status
from ninja.errors import HttpError

from organizations.api.schemas import (
    InvitationBadRequestError,
    InvitationConflictError,
    InvitationCreatePayload,
    InvitationGoneError,
    InvitationListResponse,
    InvitationNotFoundError,
    InvitationPayload,
    InvitationResponse,
    InvitationUpdateGoneError,
    InvitationUpdateNotFoundError,
    InvitationUpdateResult,
    InvitationUpdateSchema,
    MembersNotFoundError,
    OrganizationForbiddenError,
    OrganizationNotFoundError,
)
from organizations.api.views import assert_membership, organization_router
from organizations.mailpitRequests.emails import InvitationEmailError, send_invitation_email
from organizations.models import Member, OrgInvitation
from users.models import User

invitation_router = Router(tags=['Temporary Invitations'])


@organization_router.post(
    '{org_id}/invitation/create',
    response={
        201: InvitationListResponse,
        400: InvitationBadRequestError,
        403: OrganizationForbiddenError,
        404: OrganizationNotFoundError | MembersNotFoundError,
    },
)
@assert_membership
def create_invitation(request: HttpRequest, org_id: int, payload: InvitationCreatePayload) -> Status[OrgInvitation]:
    sender = Member.objects.get(user=request.user.pk, organization=org_id)
    try:
        with transaction.atomic():
            invitation = OrgInvitation.objects.create(
                org_invite_id=org_id,
                email=payload.email,
                sender_id=sender.pk,
                text_message=payload.text_message,
            )
        send_invitation_email(invitation)
    except ValidationError as exc:
        raise HttpError(400, '; '.join(exc.messages)) from exc
    except InvitationEmailError as exc:
        raise HttpError(exc.status_code, str(exc.text)) from exc
    return Status(201, invitation)


@invitation_router.get(
    '/{invite_token}',
    response={
        200: InvitationResponse,
        400: InvitationBadRequestError,
        404: InvitationNotFoundError,
        410: InvitationGoneError,
    },
)
def get_invitation(request: HttpRequest, invite_token: str) -> OrgInvitation:  # noqa: ARG001
    return OrgInvitation.objects.get_and_validate_invitation(invite_token)


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
        raise HttpError(
            404,
            f'User with email "{invitation.email}" does not exist. First create own account then login in and '
            f'try to accept again!',
        )

    member, created_bool = Member.objects.get_or_create(user=user, organization=invitation.org_invite)
    if not created_bool:
        raise HttpError(409, f'The user {user} is already invited to organization {invitation.org_invite}.')

    invitation.accepted = True
    invitation.save()
    return {'accepted': invitation.accepted, 'member': member}

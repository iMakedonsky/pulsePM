from typing import cast

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from organizations.models import Member
from users.api.schemas import (
    GetListParticipation,
    MembershipNotFoundError,
    SessionUnauthorizedError,
    UserResponse,
)
from users.models import User

router_profile = Router(tags=['Profile'])
router_membership = Router(tags=['Profile'])


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


@router_profile.get('/profile', response={200: UserResponse, 401: SessionUnauthorizedError})
def current_user(request: HttpRequest) -> User:
    return cast(AuthenticatedRequest, request).user


@router_membership.get(
    '/',
    response={200: list[GetListParticipation], 401: SessionUnauthorizedError, 404: MembershipNotFoundError},
)
def participation(request: HttpRequest) -> QuerySet[Member]:
    user = cast(AuthenticatedRequest, request).user
    membership = Member.objects.filter(user=user.pk).select_related('organization')
    if not membership.exists():
        raise HttpError(404, "User haven't participated yet.")
    return membership

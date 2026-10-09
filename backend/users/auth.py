from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError

from organizations.invitation import get_invitation, update_invitation
from organizations.schema import InvitationPayload
from users.models import User
from users.schema import (
    BadRequestError,
    ConflictError,
    GoneError,
    LoginPayload,
    NotFoundError,
    RegisterPayload,
    UnauthorizedError,
    UserResponse,
)

router = Router(tags=['Authentication'])


@router.post(
    '/register',
    response={200: UserResponse, 400: BadRequestError, 404: NotFoundError, 409: ConflictError, 410: GoneError},
)
def register_endpoint(request: HttpRequest, payload: RegisterPayload, token: str | None = None) -> User:
    try:
        validate_password(payload.password)
    except ValidationError as exc:
        raise HttpError(
            400,
            'Provided password is invalid.',
        ) from exc

    if token:
        invitation = get_invitation(request, token)['invitation']
        if invitation.email.lower() != payload.email.lower():
            raise HttpError(400, 'Registration email does not match the invitation.')

    try:
        # Atomic: if accepting the invitation fails, the new user is rolled back too.
        with transaction.atomic():
            user = User.objects.create_user(
                email=payload.email,
                password=payload.password,
            )
            if token:
                update_invitation(request, InvitationPayload(accepted=True), token)
    except ValueError as exc:
        raise HttpError(400, str(exc)) from exc
    except IntegrityError as exc:
        if User.objects.filter(email=payload.email).exists():
            raise HttpError(
                409,
                'User already exists with the same email.',
            ) from exc
        raise

    return user


@router.post('/login', response={200: UserResponse, 401: UnauthorizedError})
def login_endpoint(request: HttpRequest, payload: LoginPayload) -> User:
    user = authenticate(request, username=payload.email, password=payload.password)
    if user is None:
        raise HttpError(401, 'Invalid email or password.')
    login(request, user)
    return user


@router.post('/logout', response={204: None})
def logout_endpoint(request: HttpRequest) -> tuple[int, None]:
    logout(request)
    return 204, None

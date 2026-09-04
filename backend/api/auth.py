from typing import Self, cast

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpRequest
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import EmailStr

from users.models import User

router = Router(tags=['Authentication'])


class RegisterPayload(Schema):
    email: EmailStr
    password: str


class LoginPayload(Schema):
    email: str
    password: str


class UserResponse(Schema):
    id: int
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_user_instance(cls, user: User) -> Self:
        return cls(
            id=user.pk,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


@router.post('/register', response={200: UserResponse})
def register_endpoint(request: HttpRequest, payload: RegisterPayload) -> UserResponse | tuple[int, dict[str, str]]:
    try:
        validate_password(payload.password)
    except ValidationError as exc:
        raise HttpError(
            400,
            'Provided password is invalid.',
        ) from exc

    try:
        user = User.objects.create_user(
            email=payload.email,
            password=payload.password,
        )
    except IntegrityError as exc:
        if User.objects.filter(email=payload.email).exists():
            raise HttpError(
                409,
                'User already exists with the same email.',
            ) from exc
        raise

    login(request, user)

    return UserResponse.from_user_instance(user)


@router.post('/login', response={200: UserResponse, 401: dict})
def login_endpoint(request: HttpRequest, payload: LoginPayload) -> UserResponse | tuple[int, dict[str, str]]:
    user = authenticate(request, username=payload.email, password=payload.password)
    if user is None:
        return 401, {'detail': 'Invalid email or password.'}
    login(request, user)
    return UserResponse.from_user_instance(user)


@router.post('/logout', response={204: None})
def logout_endpoint(request: HttpRequest) -> tuple[int, None]:
    logout(request)
    return 204, None


@router.get('/auth/me', response={200: UserResponse, 401: dict})
def current_user(request: HttpRequest) -> UserResponse | tuple[int, dict[str, str]]:
    if not request.user.is_authenticated:
        return 401, {'detail': 'Authentication required.'}
    return UserResponse.from_user_instance(cast(AuthenticatedRequest, request).user)

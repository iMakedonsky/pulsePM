from typing import cast

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from ninja import Router, Schema
from pydantic import ConfigDict

from users.models import User

router = Router(tags=['Authentication'])


class LoginPayload(Schema):
    email: str
    password: str


class UserResponse(Schema):
    id: int
    email: str
    first_name: str
    last_name: str

    model_config = ConfigDict(extra='ignore')


class AuthenticatedRequest(HttpRequest):
    """A request whose user has been verified as the project's User model."""

    user: User


@router.post('/login', response={200: UserResponse, 401: dict})
def login_endpoint(request: HttpRequest, payload: LoginPayload) -> UserResponse | tuple[int, dict[str, str]]:
    user = authenticate(request, username=payload.email, password=payload.password)
    if user is None:
        return 401, {'detail': 'Invalid email or password.'}
    login(request, user)
    if user.pk is None:
        raise ValueError('Authenticated users must have a primary key.')
    return UserResponse(**user.__dict__)


@router.post('/logout', response={204: None})
def logout_endpoint(request: HttpRequest) -> tuple[int, None]:
    logout(request)
    return 204, None


@router.get('/auth/me', response={200: UserResponse, 401: dict})
def current_user(request: HttpRequest) -> UserResponse | tuple[int, dict[str, str]]:
    if not request.user.is_authenticated:
        return 401, {'detail': 'Authentication required.'}
    return UserResponse(**cast(AuthenticatedRequest, request).user.__dict__)

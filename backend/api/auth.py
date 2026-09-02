from typing import Self, cast

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpRequest
from ninja import Router, Schema

from users.models import User

router = Router(tags=['Authentication'])


class RegisterPayload(Schema):
    email: str
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


@router.post('/register', response={200: UserResponse, 400: dict})
def register_endpoint(request: HttpRequest, payload: RegisterPayload) -> UserResponse | tuple[int, dict[str, str]]:
    try:
        # Validation password is cool feature, but it slows down the development process :) If you would like to, just comment it.
        validate_password(payload.password)
        create_new_user = User.objects.create_user(email=payload.email, password=payload.password)

        login(request, create_new_user)
        return UserResponse.from_user_instance(create_new_user)
    except ValueError:
        return 400, {'detail': 'Provided email is invalid.'}
    except ValidationError:
        return 400, {'detail': 'Provided password is invalid.'}
    except IntegrityError:
        return 400, {'detail': 'User already exists with the same email.'}


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

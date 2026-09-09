from typing import Self

from ninja import Schema
from pydantic import EmailStr

from users.models import User


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

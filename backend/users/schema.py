from typing import Self

from ninja import Schema
from pydantic import AwareDatetime, EmailStr

from organizations.models import Member
from users.models import User


class UserProfileSchema(Schema):
    """If we add profile update endoit in details,
    that schema will return full user information in Organization.
    """
    avatar_url: str
    email: EmailStr
    username: str
    first_name: str
    last_name: str

class GetListParticipation(Schema):
    id: int
    organization: int
    role: str
    position: str
    last_activity: AwareDatetime

    @classmethod
    def from_participation_instance(cls, member: Member) -> Self:
        return cls(
            id=member.pk,
            organization=member.organization,
            role=member.role,
            position=member.position,
            last_activity=member.last_activity,
        )


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

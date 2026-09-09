from typing import Self

from ninja import Schema

from organizations.models import Organization


class OrganizationSchema(Schema):
    owner: int
    name: str
    description: str

    @classmethod
    def from_organization_instance(cls, org: Organization) -> Self:
        return cls(
            owner=org.pk,
            name=org.name,
            description=org.description,
        )


class MemberSchema(Schema):
    user: int
    organization: int
    role: str

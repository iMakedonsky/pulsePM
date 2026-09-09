from django.contrib.auth.models import AbstractUser
from ninja import Schema

from organizations.models import Organization


class OrganizationSchema(Schema):
    owner: AbstractUser
    name: str
    description: str

class MemberSchema(Schema):
    user: AbstractUser
    organization: Organization
    role: str

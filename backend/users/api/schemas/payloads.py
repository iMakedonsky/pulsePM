from ninja import Schema
from pydantic import EmailStr


class RegisterPayload(Schema):
    email: EmailStr
    password: str


class LoginPayload(Schema):
    email: str
    password: str

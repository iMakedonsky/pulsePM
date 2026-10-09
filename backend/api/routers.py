import logging

from django.http import HttpRequest, HttpResponse
from ninja import NinjaAPI
from ninja.errors import ValidationError
from ninja.security import SessionAuth

from organizations.api import members_router, organization_router, workspace_router
from organizations.invitation import invitation_router
from users.api import router_membership, router_profile
from users.auth import router as auth_router

description = """
A web app designed for startups, companies, and individuals
to manage projects using Agile principles. Centralize project tracking,
documentation, and reminders in one environment,
making it simple to prioritize goals,
allocate resources, and fulfill client needs.
"""
api = NinjaAPI(title='PulsePM API', version='1.0.0', description=description, auth=SessionAuth())
logger = logging.getLogger('django')


@api.exception_handler(ValidationError)
def validation_error_handler(request: HttpRequest, exc: ValidationError) -> HttpResponse:
    """Report malformed input (e.g. a non-numeric id or a bad email) as 400 instead of ninja's default 422."""
    error = exc.errors[0] if exc.errors else {}
    location = error.get('loc', ())
    field = location[-1] if location else 'data'
    if field == 'email':
        detail = 'Enter a valid email address.'
    elif location and location[0] == 'path':
        detail = f'Invalid {field}.'
    else:
        detail = f'Invalid {field}: {error.get("msg", "invalid value")}'
    return api.create_response(request, {'detail': detail}, status=400)


@api.exception_handler(Exception)
def catch_all(request: HttpRequest, exc: Exception) -> HttpResponse:
    logger.error('Unhandled exception', exc_info=exc)
    return api.create_response(
        request,
        {'detail': 'Internal server error'},
        status=500,
    )


api.add_router('/auth/', auth_router, auth=None)

router_profile.add_router('/memberships/', router_membership)
api.add_router('/user/', router_profile)

organization_router.add_router('/', workspace_router)
organization_router.add_router('/', members_router)
api.add_router('/organization/', organization_router, auth=None)

api.add_router('/invitation/', invitation_router, auth=None)

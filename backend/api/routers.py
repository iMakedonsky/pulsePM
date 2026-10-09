from ninja import NinjaAPI
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

api.add_router('/auth/', auth_router, auth=None)

router_profile.add_router('/memberships/', router_membership)
api.add_router('/user/', router_profile)

organization_router.add_router('/', workspace_router)
organization_router.add_router('/', members_router)
api.add_router('/organization/', organization_router)

api.add_router('/invitation/', invitation_router, auth=None)

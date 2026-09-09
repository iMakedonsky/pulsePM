from ninja import NinjaAPI
from ninja.security import SessionAuth

from organizations.api import router as organization_router
from users.api import router_membership, router_profile
from users.auth import router as auth_router

# class AuthBearer(HttpBearer):
#     def authenticate(self, request, token):
#         if token == 'supersecret':
#             return token


description = """
A web app designed for startups, companies, and individuals 
to manage projects using Agile principles. Centralize project tracking, 
documentation, and reminders in one environment, 
making it simple to prioritize goals, 
allocate resources, and fulfill client needs.
"""
api = NinjaAPI(title='PulsePM API', version='1.0.0', description=description)

api.add_router('/auth/', auth_router)
router_profile.add_router('/memberships/', router_membership, auth=SessionAuth())
api.add_router('/user/', router_profile, auth=SessionAuth())
api.add_router('/organization/', organization_router, auth=SessionAuth())

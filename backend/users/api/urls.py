"""Router wiring for the users API; mounted by `api.routers`."""

from users.api.auth_views import router as auth_router
from users.api.profile_views import router_membership, router_profile

router_profile.add_router('/memberships/', router_membership)

__all__ = ['auth_router', 'router_profile']

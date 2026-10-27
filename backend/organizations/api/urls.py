"""Router wiring for the organizations API; mounted by `api.routers`."""

from organizations.api.invitation_views import invitation_router
from organizations.api.views import members_router, organization_router, workspace_router

organization_router.add_router('/', workspace_router)
organization_router.add_router('/', members_router)

__all__ = ['invitation_router', 'organization_router']

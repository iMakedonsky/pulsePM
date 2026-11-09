"""Router wiring for the work items API; mounted by `api.routers`."""

from organizations.api.workspace_views import workspace_router
from workitems.api.views import workitem_router

workspace_router.add_router('/', workitem_router)

__all__ = ['workitem_router']

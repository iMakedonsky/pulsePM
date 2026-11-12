"""Router wiring for the work items API; mounted by `api.routers`."""

from workitems.api.views import workitem_router

__all__ = ['workitem_router']

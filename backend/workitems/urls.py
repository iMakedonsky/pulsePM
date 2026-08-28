from django.urls import path

from . import views

urlpatterns = [
    path(
        'organization/<int:organization_id>/workspace/<int:workspace_id>/',
        views.WorkSpaceView.as_view(),
        name='workspace',
    ),
    path(
        'organization/<int:organization_id>/workspace/<int:workspace_id>/workitem/<int:workitem_id>/',
        views.WorkItemView.as_view(),
        name='workitem',
    ),
    path(
        'organization/<int:organization_id>/workspace/<int:workspace_id>/workitem/<int:workitem_id>/delete/',
        views.DeleteWorkItem.as_view(),
        name='workitem_delete',
    ),
]

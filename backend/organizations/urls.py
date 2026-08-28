from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    path('organization/<int:organization_id>/', views.OrganizationView.as_view(), name='organization'),
    path('organization/<int:organization_id>/delete/', views.DeleteOrganization.as_view(), name='organization_delete'),
    path('organization/<int:organization_id>/member/<int:member_id>/', views.MemberView.as_view(), name='profile'),
    path(
        'organization/<int:organization_id>/member/<int:member_id>/delete/',
        views.DeleteMemberProfile.as_view(),
        name='member_delete',
    ),
    path(
        'organization/<int:organization_id>/workspace/<int:workspace_id>/delete/',
        views.DeleteWorkspace.as_view(),
        name='workspace_delete',
    ),
]

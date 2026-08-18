from django.urls import path
from . import views

app_name = "pulse"
urlpatterns = [
    # path('', views.Home.as_view(), name='index'),
    path('', views.HomePage.as_view(), name='index'),
    path('organization/<int:pk>', views.Org.as_view(), name='organization'),
    path('organization/workspace/<int:pk>', views.Space.as_view(), name='workspace'),
    path("organization/workspace/<int:pk>/delete/", views.DeleteWorkspace.as_view(), name='workspace_delete'),
    path('organization/member_profile/<int:pk>/delete/', views.DeleteMemberProfile.as_view(), name='profile_delete'),
    path('organization/member_profile/<int:pk>', views.ProfileMember.as_view(), name='profile'),
    path('organization/workspaces/workitem/<int:pk>', views.Item.as_view(), name='workitem'),
 ]

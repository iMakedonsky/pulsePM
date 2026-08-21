from django.urls import path
from . import views

app_name = "pulse"
urlpatterns = [
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/sign-up', views.RegistrationView.as_view(), name='registration'),
    path('', views.HomePageView.as_view(), name='index'),
    path('organization/<int:pk>', views.OrganizationView.as_view(), name='organization'),
    path('organization/workspace/<int:pk>', views.WorkSpaceView.as_view(), name='workspace'),
    path("organization/workspace/<int:pk>/delete/", views.DeleteWorkspace.as_view(), name='workspace_delete'),
    path('organization/member/<int:pk>/delete/', views.DeleteMemberProfile.as_view(), name='profile_delete'),
    path('organization/member/profile/<int:pk>', views.MemberView.as_view(), name='profile'),
    path('organization/workspaces/workitem/<int:pk>', views.WorkItemView.as_view(), name='workitem'),
 ]

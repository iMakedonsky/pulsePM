from django.urls import path
from . import views

app_name = "pulse"
urlpatterns = [
    path('', views.Home.as_view(), name='index'),
    path('organization/<int:pk>', views.Org.as_view(), name='organization'),
    path('organization/member_profile/<int:pk>', views.Profile.as_view(), name='profile'),
    path('organization/workspace/<int:pk>', views.Space.as_view(), name='workspace'),
    path('organization/workspaces/workitem/<int:pk>', views.Item.as_view(), name='workitem'),
 ]
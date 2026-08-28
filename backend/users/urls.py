from django.urls import path

from . import views

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/signup/', views.RegistrationView.as_view(), name='signup'),
    path('auth/logout/', views.logout_view, name='logout'),
]

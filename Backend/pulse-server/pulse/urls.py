from django.urls import include, path

from . import views

urlpatterns = [
    path("auth/login", views.LoginView.as_view(), name="login"),
    path("auth/sign-up", views.RegistrationView.as_view(), name="registration"),
    path("", views.HomePageView.as_view(), name="index"),
    path(
        "organization/<int:organization_id>/",
        include(
            [
                path("", views.OrganizationView.as_view(), name="organization"),
                path(
                    "member/<int:member_id>/",
                    include(
                        [
                            path(
                                "",
                                views.MemberView.as_view(),
                                name="profile",
                            ),
                            path(
                                "delete/",
                                views.DeleteMemberProfile.as_view(),
                                name="member_delete",
                            ),
                        ]
                    ),
                ),
                path(
                    "workspace/<int:workspace_id>/",
                    include(
                        [
                            path("", views.WorkSpaceView.as_view(), name="workspace"),
                            path(
                                "delete/",
                                views.DeleteWorkspace.as_view(),
                                name="workspace_delete",
                            ),
                            path(
                                "workitem/<int:workitem_id>/",
                                views.WorkItemView.as_view(),
                                name="workitem",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]

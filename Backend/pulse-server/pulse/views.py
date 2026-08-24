from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View
from pulse.models import *

from .forms import (
    AddItemForm,
    CreateWorkspaceForm,
    OrganizationNonModelForm,
    RegistrationForm,
)

# TODO: finish statistic endpoint (figure out with approach) & implement each org specific statistic
# TODO: implement hidden/collaps button, that allows to create an entity of that kind (for each page)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pulse/auth.html",
            {
                "login_form": AuthenticationForm(),
            },
        )

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request=request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                return redirect('auth/login')
        return render(
            request,
            'pulse/auth.html',
            {'login_form': form,
        })


class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pulse/sign-up.html",
            {
                "registration_form": RegistrationForm(),
            },
        )

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(data=request.POST)

        if form.is_valid():
            try:
                user = User.objects.create_user(
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                )
            except IntegrityError:
                return HttpResponse(status=409, content="User already exists")
            return redirect("/auth/login")

        return render(
            request,
            "pulse/sign-up.html",
            {
                "registration_form": form,
            },
        )

def logout_view(request):
    logout(request)
    return redirect(to='login')

class HomePageView(LoginRequiredMixin, View):
    login_url = "auth/login"
    redirect_field_name = "redirect_to"

    def get(self, request, *args, **kwargs):

        general_statistic = {
            "organizations": Organization.objects.count(),
            "workspaces": WorkSpace.objects.count(),
            "workitems": WorkItem.objects.count(),
            "members": Member.objects.count(),
        }

        # for key in data_keys:
        #     for org in Organization.objects.all():
        #

        return render(
            request,
            "pulse/index.html",
            {
                "organization_form": OrganizationNonModelForm(),
                "organization_list": Organization.objects.all(),
                "general_statistic_rows": general_statistic
            },
        )

    def post(self, request, *args, **kwargs):
        form = OrganizationNonModelForm(request.POST)
        if form.is_valid():
            new_organization = Organization.objects.create(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                owner_id=int(form.cleaned_data["owner"]),
            )

            Member.objects.create(
                organization_id=new_organization.id,
                user_id=form.cleaned_data["owner"],
                role='owner')

            messages.success(
                request, f"Organization {new_organization.name} created successfully"
            )
            return redirect(request.path_info)

        return render(
            request,
            "pulse/index.html",
            {
                "organization_form": form,
                "organization_list": Organization.objects.all(),
            },
        )

# class GeneralReportView(View):
#     def get(self, request, *args, **kwargs):
#         data_keys = ["workspaces", "workitems", "members"]
#
#         # for key in data_keys:
#         #     for org in Organization.objects.all():
#         #
#
#         general_statistic = {
#             "organizations": Organization.objects.count(),
#             "workspaces": WorkSpace.objects.count(),
#             "workitems": WorkItem.objects.count(),
#             "members": Member.objects.count(),
#         }
#
#         return render(
#             request,
#             'pulse/index.html',
#             {
#                 "general_statistic_rows": general_statistic
#             }
#         )

class OrganizationView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pulse/organization.html",
            {
                "workspace_form": CreateWorkspaceForm(),
                "workspace_list": WorkSpace.objects.filter(
                    organization_id=kwargs["organization_id"]
                ),
                "member_list": Member.objects.filter(
                        organization_id=kwargs["organization_id"],
                        role__in=["contributor", "project-manager"]
                ),
                "owner": Member.objects.get(
                    organization_id=kwargs["organization_id"],
                    role="owner")
            },
        )


    def post(self, request, *args, **kwargs):
        form = CreateWorkspaceForm(request.POST)
        org_id = kwargs["organization_id"]
        if form.is_valid():
            create_workspace = WorkSpace.objects.create(
                name=form.cleaned_data["name"],
                organization_id=kwargs["organization_id"],
                created_by=Member.objects.get_or_create(
                    organization_id=org_id,
                    user=request.user,
                )[0],
                space_code=form.cleaned_data["space_code"],
                description=form.cleaned_data["description"],
                icon_url="",
            )
            messages.success(
                request, f"Workspace {create_workspace.name} created successfully"
            )
            return redirect(request.path_info)

        return render(
            request,
            "pulse/organization.html",
            {
                "workspace_form": form,
                "workspace_list": WorkSpace.objects.filter(organization_id=org_id),
                "member_list": Member.objects.filter(organization_id=org_id),
            },
        )


class WorkSpaceView(View):
    def get(self, request, *args, **kwargs):
        workspace_id = self.kwargs.get("workspace_id")

        return render(
            request,
            "pulse/workspace.html",
            {
                "workitem_form": AddItemForm(),
                "workspace_data": get_object_or_404(WorkSpace, pk=workspace_id),
                "workitem_list": WorkItem.objects.filter(workspace_id=workspace_id),
            },
        )

    def post(self, request, *args, **kwargs):
        form = AddItemForm(request.POST)
        org_id = kwargs["organization_id"]
        workspace_id = kwargs["workspace_id"]

        if form.is_valid():
            try:
                new_workitem = WorkItem.objects.create(
                    title=form.cleaned_data["title"],
                    workspace_id=workspace_id,
                    created_by=Member.objects.get_or_create(
                        user=request.user, organization_id=org_id
                    )[0],
                    assigned_to_id=int(form.cleaned_data["assignee"]),
                    description=form.cleaned_data["description"],
                    status=form.cleaned_data["status"],
                    priority=form.cleaned_data["priority"],
                    estimated_time=form.cleaned_data["estimate"],
                    time_spent=form.cleaned_data["spent"],
                    due_date=form.cleaned_data["due_date"]
                )
                messages.success(
                    request, f"WorkItem {new_workitem.title} created successfully"
                )
            except ValidationError:
                return HttpResponse(status=400, content="The due date cannot be in the past.")
            return redirect(request.path_info)

        return render(
            request,
            "pulse/workspace.html",
            {
                "workitem_form": form,
                "workitem_list": WorkItem.objects.filter(workspace_id=workspace_id),
            },
        )


class MemberView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pulse/profile.html",
            {
                "profile_data": get_object_or_404(Member, pk=kwargs["member_id"]),
            },
        )


class WorkItemView(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "pulse/workitem.html",
            {
                "workitem_data": get_object_or_404(WorkItem, pk=kwargs["workitem_id"]),
            },
        )


class DeleteOrganization(View):
    def post(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, pk=kwargs["organization_id"])
        organization.delete()

        return redirect(to='/')

class DeleteWorkspace(View):
    def post(self, request, *args, **kwargs):
        workspace = get_object_or_404(WorkSpace, pk=kwargs["workspace_id"])
        workspace.delete()

        return redirect(reverse(
            'organization',
            kwargs={
                'organization_id': kwargs["organization_id"]}
        ))

class DeleteMemberProfile(View):
    def post(self, request, *args, **kwargs):
        member = get_object_or_404(Member, pk=kwargs["member_id"])
        member.delete()

        return redirect(reverse(
            'organization',
            kwargs={
                'organization_id': kwargs["organization_id"]}
        ))

class DeleteWorkItem(View):
    def post(self, request, *args, **kwargs):
        workitem = get_object_or_404(WorkItem, pk=kwargs["workitem_id"])
        workitem.delete()

        return redirect(reverse(
            'workspace',
            kwargs={
                'organization_id': kwargs["organization_id"],
                'workspace_id': kwargs["workspace_id"]}
        ))
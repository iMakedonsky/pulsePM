from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View

from users.models import User
from workitems.models import WorkItem

from .forms import CreateWorkspaceForm, OrganizationNonModelForm
from .models import Member, Organization, WorkSpace


class HomePageView(LoginRequiredMixin, View):
    login_url = 'auth/login'
    redirect_field_name = 'redirect_to'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        general_statistic = {
            'organizations': Organization.objects.count(),
            'workspaces': WorkSpace.objects.count(),
            'workitems': WorkItem.objects.count(),
            'members': Member.objects.count(),
        }
        each_org_statistic = {
            organization.name: {
                'workspaces': WorkSpace.objects.filter(organization=organization).count(),
                'workitems': WorkItem.objects.filter(workspace__organization=organization).count(),
                'members': Member.objects.filter(organization=organization).count(),
            }
            for organization in Organization.objects.all()
        }
        return render(
            request,
            'pulse/index.html',
            {
                'organization_form': OrganizationNonModelForm(),
                'organization_list': Organization.objects.all(),
                'general_statistic_rows': general_statistic,
                'each_org_statistic': each_org_statistic,
            },
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = OrganizationNonModelForm(request.POST)
        if form.is_valid():
            organization = Organization.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                owner_id=int(form.cleaned_data['owner']),
            )
            Member.objects.create(
                organization=organization, user_id=form.cleaned_data['owner'], role=Member.OrgRoles.OWNER
            )
            messages.success(request, f'Organization {organization.name} created successfully')
            return redirect(request.path_info)
        return render(
            request, 'pulse/index.html', {'organization_form': form, 'organization_list': Organization.objects.all()}
        )


class OrganizationView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        organization_id = kwargs['organization_id']
        return render(
            request,
            'pulse/organization.html',
            {
                'workspace_form': CreateWorkspaceForm(),
                'workspace_list': WorkSpace.objects.filter(organization_id=organization_id),
                'member_list': Member.objects.filter(
                    organization_id=organization_id,
                    role__in=[Member.OrgRoles.CONTRIBUTOR, Member.OrgRoles.PM],
                ),
                'owner': Member.objects.get(organization_id=organization_id, role=Member.OrgRoles.OWNER),
            },
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = CreateWorkspaceForm(request.POST)
        organization_id = kwargs['organization_id']
        if form.is_valid():
            creator, _ = Member.objects.get_or_create(
                organization_id=organization_id,
                user=cast(User, request.user),
            )
            workspace = WorkSpace.objects.create(
                name=form.cleaned_data['name'],
                organization_id=organization_id,
                created_by=creator,
                space_code=form.cleaned_data['space_code'],
                description=form.cleaned_data['description'],
                icon_url='',
            )
            messages.success(request, f'Workspace {workspace.name} created successfully')
            return redirect(request.path_info)
        return render(
            request,
            'pulse/organization.html',
            {
                'workspace_form': form,
                'workspace_list': WorkSpace.objects.filter(organization_id=organization_id),
                'member_list': Member.objects.filter(organization_id=organization_id),
            },
        )


class MemberView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(
            request, 'pulse/profile.html', {'profile_data': get_object_or_404(Member, pk=kwargs['member_id'])}
        )


class DeleteOrganization(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        get_object_or_404(Organization, pk=kwargs['organization_id']).delete()
        return redirect(to='/')


class DeleteWorkspace(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        get_object_or_404(WorkSpace, pk=kwargs['workspace_id']).delete()
        return redirect(reverse('organization', kwargs={'organization_id': kwargs['organization_id']}))


class DeleteMemberProfile(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        get_object_or_404(Member, pk=kwargs['member_id']).delete()
        return redirect(reverse('organization', kwargs={'organization_id': kwargs['organization_id']}))

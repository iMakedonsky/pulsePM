from datetime import timezone as none_django_timezone
from django.utils.dateparse import parse_datetime

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View

from .forms import OrganizationNonModelForm, CreateWorkspaceForm, AddItemForm
from pulse.models import *


class HomePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pulse/index.html',{
                'organization_form': OrganizationNonModelForm(),
                'organization_list': Organization.objects.all(),
            }
        )

    def post(self, request, *args, **kwargs):
        form = OrganizationNonModelForm(request.POST)

        if form.is_valid():
            new_organization = Organization.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                owner_id=int(form.cleaned_data['owner']),
            )
            messages.success(request, f"Organization {new_organization.name} created successfully")
            return redirect(request.path_info)

        return render(request, 'pulse/index.html',{
            'organization_form': form,
            'organization_list': Organization.objects.all(),
        })

class OrganizationView(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        return render(request, 'pulse/organization.html',{
            'workspace_form': CreateWorkspaceForm(),
            'workspace_list': WorkSpace.objects.filter(organization_id=pk),
            'member_list': Member.objects.filter(organization_id=pk),
        })

    def post(self, request, *args, **kwargs):
        form = CreateWorkspaceForm(request.POST)
        pk = self.kwargs.get("pk")

        if form.is_valid():
            create_workspace = WorkSpace.objects.create(
                name=form.cleaned_data['name'],
                organization_id=pk,
                created_by=Member.objects.get(id=1), # hardcoded I have fed organization id as value to member_id
                space_code=form.cleaned_data['space_code'],
                description=form.cleaned_data['description'],
                icon_url="",
            )
            messages.success(request, f"Workspace {create_workspace.name} created successfully")
            return redirect(request.path_info)

        return render(request, 'pulse/organization.html',{
            'workspace_form': form,
            'workspace_list': WorkSpace.objects.filter(organization_id=pk),
            'member_list': Member.objects.filter(organization_id=pk),
        })

class WorkSpaceView(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        return render(request, 'pulse/workspace.html', {
            'workitem_form': AddItemForm(),
            'workspace_data': get_object_or_404(WorkSpace, pk=pk),
            'workitem_list': WorkItem.objects.filter(workspace_id=pk),
        })

    def post(self, request, *args, **kwargs):
        form = AddItemForm(request.POST)
        pk = self.kwargs.get("pk")

        if form.is_valid():
            new_workitem = WorkItem.objects.create(
                title=form.cleaned_data['title'],
                workspace_id=pk,
                created_by=Member.objects.get(id=1),  # hardcoded I have fed workspace id as value to member_id (user = request.user, organization__workspace__id = pk)
                assigned_to_id=int(form.cleaned_data['assignee']),
                description=form.cleaned_data['description'],
                status=form.cleaned_data['status'],
                priority=form.cleaned_data['priority'],
                estimated_time=form.cleaned_data['estimate'],
                time_spent=form.cleaned_data['spent'],
                due_date=parse_datetime(form.cleaned_data["due_date"]).replace(tzinfo=none_django_timezone.utc),
            )
            messages.success(request, f"WorkItem {new_workitem.title} created successfully")
            return redirect(request.path_info)

        return render(request, 'pulse/workspace.html',{
            'workitem_form': form,
            'workitem_list': WorkItem.objects.filter(workspace_id=pk),
        })

class MemberView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pulse/profile.html', {
            'profile_data': get_object_or_404(Member, pk=kwargs["pk"]),
        })


class WorkItemView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pulse/workitem.html', {
            'workitem_data': get_object_or_404(WorkItem, pk=kwargs["pk"]),
        })


class DeleteWorkspace(View):
    def post(self, request, *args, **kwargs):
        workspace = get_object_or_404(WorkSpace, pk=kwargs["pk"])
        workspace.delete()

        return redirect(request.path_info)

class DeleteMemberProfile(View):
    def post(self, request, *args, **kwargs):
        member = get_object_or_404(Member, pk=kwargs["pk"])
        member.delete()

        return redirect(request.path_info)
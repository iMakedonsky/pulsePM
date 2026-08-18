from datetime import timedelta
from django.utils.dateparse import parse_datetime
from keyword import kwlist
from tarfile import NUL

from django.contrib import messages
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views import generic
from django.http import JsonResponse
from django import forms
from django.views.generic import FormView
from django.views.generic.base import View
from psycopg.sql import NULL

from .forms import OrganizationNonModelForm, CreateWorkspaceForm, AddItemForm
from pulse.models import *


class HomePage(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pulse/index.html',{
                'form': OrganizationNonModelForm(),
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
            return redirect('/')

        return render(request, 'pulse/index.html',{
            'form': form,
            'organization_list': Organization.objects.all(),
        })

class Org(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        return render(request, 'pulse/organization.html',{
            'form': CreateWorkspaceForm(),
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
                description=form.cleaned_data['description']
            )
            messages.success(request, f"Workspace {create_workspace.name} created successfully")
            return redirect('/')

        return render(request, 'pulse/organization.html',{
            'form': form,
            'workspace_list': WorkSpace.objects.filter(organization_id=pk),
        })

class Space(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")

        return render(request, 'pulse/workspace.html', {
            'form': AddItemForm(),
            'workspace_data': WorkSpace.objects.get(id=pk),
            'workitem_list': WorkItem.objects.filter(workspace_id=pk),
        })

    def post(self, request, *args, **kwargs):
        form = AddItemForm(request.POST)
        pk = self.kwargs.get("pk")

        if form.is_valid():
            new_workitem = WorkItem.objects.create(
                title=form.cleaned_data['title'],
                workspace_id=pk,
                created_by=Member.objects.get(id=1),  # hardcoded I have fed workspace id as value to member_id
                assigned_to=Member.objects.get(id=int(form.cleaned_data['assignee'])),
                description=form.cleaned_data['description'],
                status=form.cleaned_data['status'],
                priority=form.cleaned_data['priority'],
                estimated_time=form.cleaned_data['estimate'],
                time_spent=form.cleaned_data['spent'],
                due_date=parse_datetime(f'{form.cleaned_data["due_date"]}T18:00:00+02:00')
            )
            messages.success(request, f"WorkItem {new_workitem.title} created successfully")
            return redirect('/')

        return render(request, 'pulse/workspace.html',{
            'form': form,
            'workspace_list': WorkSpace.objects.filter(workspace_id=pk),
        })

class ProfileMember(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'pulse/profile.html', {
            'profile_data': Member.objects.get(pk=kwargs["pk"]),
        })


class DeleteWorkspace(View):
    def post(self, request, *args, **kwargs):
        workspace = get_object_or_404(WorkSpace, pk=kwargs["pk"])
        workspace.delete()

        return redirect('/')


class DeleteMemberProfile(View):
    def post(self, request, *args, **kwargs):
        member = get_object_or_404(Member, pk=kwargs["pk"])
        member.delete()

        return redirect('/')

class Item(generic.DeleteView):
    model = WorkItem

    template_name = "pulse/workitem.html"
    context_object_name = "workitem_data"

    def get_queryset(self):
        return WorkItem.objects.filter(id=self.kwargs.get("pk"))


# TODO ? : 'form has no errors' which are "errors" of form talking about?

# def create_workspace(request):
#     form = CreateWorkspaceForm()
    # if request.method == "POST":
    # return render(request, 'pulse/organization.html', {"form": form})

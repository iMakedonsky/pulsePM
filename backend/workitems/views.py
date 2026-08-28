from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import View

from organizations.models import Member, WorkSpace
from users.models import User

from .forms import AddItemForm
from .models import WorkItem


class WorkSpaceView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        workspace_id = kwargs['workspace_id']
        return render(
            request,
            'pulse/workspace.html',
            {
                'workitem_form': AddItemForm(),
                'workspace_data': get_object_or_404(WorkSpace, pk=workspace_id),
                'workitem_list': WorkItem.objects.filter(workspace_id=workspace_id),
            },
        )

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = AddItemForm(request.POST)
        organization_id = kwargs['organization_id']
        workspace_id = kwargs['workspace_id']
        if form.is_valid():
            try:
                creator, _ = Member.objects.get_or_create(
                    user=cast(User, request.user),
                    organization_id=organization_id,
                )
                workitem = WorkItem.objects.create(
                    title=form.cleaned_data['title'],
                    workspace_id=workspace_id,
                    created_by=creator,
                    assigned_to_id=int(form.cleaned_data['assignee']),
                    description=form.cleaned_data['description'],
                    status=form.cleaned_data['status'],
                    priority=form.cleaned_data['priority'],
                    estimated_time=form.cleaned_data['estimate'],
                    time_spent=form.cleaned_data['spent'],
                    due_date=form.cleaned_data['due_date'],
                )
                messages.success(request, f'WorkItem {workitem.title} created successfully')
            except ValidationError:
                messages.error(request, 'The due date cannot be in the past')
            return redirect(request.path_info)
        return render(
            request,
            'pulse/workspace.html',
            {
                'workitem_form': form,
                'workspace_data': get_object_or_404(WorkSpace, pk=workspace_id),
                'workitem_list': WorkItem.objects.filter(workspace_id=workspace_id),
            },
        )


class WorkItemView(View):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return render(
            request, 'pulse/workitem.html', {'workitem_data': get_object_or_404(WorkItem, pk=kwargs['workitem_id'])}
        )


class DeleteWorkItem(View):
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        get_object_or_404(WorkItem, pk=kwargs['workitem_id']).delete()
        return redirect(
            reverse(
                'workspace',
                kwargs={'organization_id': kwargs['organization_id'], 'workspace_id': kwargs['workspace_id']},
            )
        )

from django.shortcuts import render
from django.views import generic
from django import forms

from .forms import *
from pulse.models import *

class Home(generic.ListView):
    template_name = "pulse/index.html"
    context_object_name = "list_organizations"

    def get_queryset(self):
        return Organization.objects.all()

class Org(generic.ListView):
    model = Organization
    template_name = "pulse/organization.html"
    context_object_name = "organization_data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get("pk")

        context["workspaces_list"] = WorkSpace.objects.filter(organization=pk)
        context["members_list"] = Member.objects.filter(organization=pk)
        return context

class Space(generic.ListView):
    model = WorkSpace
    template_name = "pulse/workspace.html"
    context_object_name = "workspace_data"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get("pk")

        context["specific_workspace"] = WorkSpace.objects.get(id=pk)
        context["workitems_list"] = WorkItem.objects.filter(workspace=pk)
        return context

class Item(generic.DeleteView):
    model = WorkItem

    template_name = "pulse/workitem.html"
    context_object_name = "workitem_data"

    def get_queryset(self):
        return WorkItem.objects.filter(id=self.kwargs.get("pk"))

class Profile(generic.DeleteView):
    model = Member
    template_name = "pulse/profile.html"
    context_object_name = "profile_data"

    def get_queryset(self):
        return Member.objects.filter(id=self.kwargs.get("pk"))

# TODO: - functional views only for workspace detail page and work item page.
# TODO: - each list page should have a button that will open up a collapsed/hidden form, that allows to create an entity of that kind.
# TODO: - each detail entity link should have a delete button next to it.

# def create_workspace(request):
#     form = CreateWorkspaceForm()
#     # if request.method == "POST":
#     return render(request, 'pulse/organization.html', {"form": form})
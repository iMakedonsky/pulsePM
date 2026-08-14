from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django import forms

from .forms import OrganizationForm, OrganizationNonModelForm
from pulse.models import *

# class Home(generic.ListView, generic.CreateView):
#     template_name = "pulse/index.html"
#     context_object_name = "list_organizations"
#
#     # def get_queryset(self):
#     #     return Organization.objects.all()
#
#     def get_context_data(self, **kwargs):
#         return {
#             "list_organizations": Organization.objects.all(),
#             "current_time": timezone.now(),
#             "total_users_in_database": Member.objects.count()
#         }
#
#     def post(self, request, *args, **kwargs):
#         form = OrganizationForm(request.POST)
#         if form.is_valid():
#             Organization.objects.create(
#                 name=form.cleaned_data["name"],
#                 description=form.cleaned_data["description"],
#                 owner=request.user
#             )
#             messages.success(request, f"Organization {form.cleaned_data['name']} created successfully")
#             return self.render_to_response(self.get_context_data())
#
#         return "Success"
#         return render(request, self.template_name, {"form": form})


def home_view(request):
    context = {}
    if request.method == 'POST':
        form = OrganizationNonModelForm(request.POST)
        if form.is_valid():
            new_organization = Organization.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                owner_id=int(form.cleaned_data['owner']),
            )
            # form.cleaned_data == {'name': 'kajsdkjakjsd', 'description': 'boasodjals', 'owner_id': '1'}
            messages.success(request, f"Organization {new_organization.name} created successfully")
            form = OrganizationNonModelForm()
    else:
        form = OrganizationNonModelForm()

    context['form'] = form
    context['organizations'] = Organization.objects.all()

    return render(request, "pulse/index.html", context)







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
    # if request.method == "POST":
    # return render(request, 'pulse/organization.html', {"form": form})

from django import forms
from django.contrib.auth.models import User

from pulse.models import Member, Organization, WorkItem


def get_choices_for_account():
    return [("", "--blank--")] + [
        (account.id, account.username) for account in User.objects.all()
    ]


def get_choices_for_member():
    org = Organization.objects.all()
    members = Member.objects.all()
    return [("", "--blank--")] + [
        (member.id, member.user.username) for member in Member.objects.all()
    ]


def get_choices_for_status():
    return [("", "--blank--")] + [
        (s, s) for s in [status for status in WorkItem.Status]
    ]


def get_choices_for_priority():
    return [("", "--blank--")] + [
        (p, p) for p in [priority for priority in WorkItem.Priority]
    ]


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=50,
        required=False,
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=50,
        required=False,
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), max_length=50
    )
    email = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}), max_length=50
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}), min_length=6
    )


class OrganizationNonModelForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100)
    description = forms.CharField(
        widget=forms.Textarea(), max_length=500, required=False
    )
    owner = forms.ChoiceField(choices=get_choices_for_account, required=True)


class CreateWorkspaceForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100, required=True)
    space_code = forms.CharField(widget=forms.TextInput(), max_length=5, required=True)
    description = forms.CharField(widget=forms.Textarea(), max_length=500)


class AddItemForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=100,
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"})
    )
    assignee = forms.ChoiceField(choices=get_choices_for_member, required=True)
    status = forms.ChoiceField(choices=get_choices_for_status, required=True)
    priority = forms.ChoiceField(choices=get_choices_for_priority, required=True)
    estimate = forms.IntegerField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    spent = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control"}))
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "clase": "form-control"}), input_formats=["%Y-%m-%d"]
    )

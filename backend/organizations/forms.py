from django import forms
from django.contrib.auth import get_user_model

Choice = tuple[str, str]


def get_choices_for_account() -> list[Choice]:
    return [('', '--blank--')] + [(str(user.pk), user.email) for user in get_user_model().objects.all()]


class OrganizationNonModelForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100)
    description = forms.CharField(widget=forms.Textarea(), max_length=500, required=False)
    owner = forms.ChoiceField(choices=get_choices_for_account, required=True)


class CreateWorkspaceForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100, required=True)
    space_code = forms.CharField(widget=forms.TextInput(), max_length=5, required=True)
    description = forms.CharField(widget=forms.Textarea(), max_length=500)

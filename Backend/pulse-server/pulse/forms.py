from django import forms

from pulse.models import Account, Member


def get_choices_for_account():
    return [('', '--blank--')] + [

        (account.id, account.username)
        for account in Account.objects.all()
    ]

def get_choices_for_member():
    return [('', '--blank--')] + [

        (member.id, member.user.username)
        for member in Member.objects.all() # hardcoded. I haven't known how get members from specific ofg yet
    ]

def get_choices_for_status():
    statuses = ['review','to do','in progress','done', 'test', 'test done']
    return [('', '--blank--')] + [(s, s) for s in statuses]

def get_choices_for_priority():
    statuses = ['low','medium','high','major']
    return [('', '--blank--')] + [(s, s) for s in statuses]

class CreateWorkspaceForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100, required=True)
    space_code = forms.CharField(widget=forms.TextInput(), max_length=5, required=True)
    description = forms.CharField(widget=forms.Textarea(), max_length=500)


class AddItemForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    assignee = forms.ChoiceField(choices=get_choices_for_member, required=True)
    status = forms.ChoiceField(choices=get_choices_for_status, required=True)
    priority = forms.ChoiceField(choices=get_choices_for_priority, required=True)
    estimate = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}))
    spent = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}))
    due_date = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'2026-11-14'}))


class OrganizationNonModelForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100)
    description = forms.CharField(widget=forms.Textarea(), max_length=500, required=False)
    owner = forms.ChoiceField(choices=get_choices_for_account, required=True)

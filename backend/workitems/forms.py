from django import forms

from organizations.models import Member

from .models import WorkItem

Choice = tuple[str, str]


def get_choices_for_member() -> list[Choice]:
    return [('', '--blank--')] + [(str(member.pk), member.user.email) for member in Member.objects.all()]


def get_choices_for_status() -> list[Choice]:
    return [('', '--blank--')] + [(status.value, str(status.label)) for status in WorkItem.Status]


def get_choices_for_priority() -> list[Choice]:
    return [('', '--blank--')] + [(priority.value, str(priority.label)) for priority in WorkItem.Priority]


class AddItemForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    assignee = forms.ChoiceField(choices=get_choices_for_member, required=True)
    status = forms.ChoiceField(choices=get_choices_for_status, required=True)
    priority = forms.ChoiceField(choices=get_choices_for_priority, required=True)
    estimate = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    spent = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
    )

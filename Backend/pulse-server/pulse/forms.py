from django import forms

from pulse.models import Organization, Account


class CreateWorkspaceForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100, required=True)
    space_code = forms.CharField(widget=forms.TextInput(), max_length=5, required=True)
    description = forms.CharField(widget=forms.Textarea(), max_length=500)


class AddItemForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    # assignee = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'})))
    status = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), max_length=20, required=True)
    priority = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), max_length=20, required=True)
    estimate = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}))
    spent = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control'}))



class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'description', 'owner')

def get_choices_for_account():
    return [('', '--blank--')] + [

        (account.id, account.username)
        for account in Account.objects.all()
    ]

class OrganizationNonModelForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(), max_length=100)
    description = forms.CharField(widget=forms.Textarea(), max_length=500, required=False)
    # owner = forms.ModelChoiceField(queryset=Account.objects.all())
    owner = forms.ChoiceField(choices=get_choices_for_account, required=True)

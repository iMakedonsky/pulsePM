from django import forms


class RegistrationForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=50, required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), max_length=50, required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), max_length=254)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), min_length=6)

from django import forms
from .models import Addresses


class AddressForm(forms.ModelForm):
    class Meta:
        model = Addresses
        exclude = ('user', 'email')

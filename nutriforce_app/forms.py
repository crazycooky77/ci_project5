from django import forms
from .models import Addresses, SavedItems


class AddressForm(forms.ModelForm):
    class Meta:
        model = Addresses
        exclude = ('user',)

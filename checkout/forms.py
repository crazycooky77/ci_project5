from django import forms
from django.forms import HiddenInput
from profiles.models import Addresses


class OrderFormAddr(forms.ModelForm):
    class Meta:
        model = Addresses
        fields = ('first_name', 'last_name', 'email', 'phone_nr',
                  'addr_line1', 'addr_line2', 'addr_line3', 'city',
                  'eir_code', 'county', 'country')

    def __init__(self, *args, **kwargs):
        user_auth = kwargs.pop('user_auth', None)
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'addr_line1': 'Address Line 1',
            'addr_line2': 'Address Line 2',
            'addr_line3': 'Address Line 3',
            'city': 'City',
            'eir_code': 'Eir Code',
            'county': 'County',
            'country': 'Country',
            'email': 'Email Address',
            'phone_nr': 'Phone Number'
        }
        self.fields['first_name'].widget.attrs['autofocus'] = True
        self.fields['country'].widget.attrs['disabled'] = True
        if user_auth:
            self.fields['email'].widget = HiddenInput()
        for field in self.fields:
            placeholder = placeholders[field]
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-input'
            self.fields[field].widget.attrs['aria-label'] = placeholder
            self.fields[field].label = False

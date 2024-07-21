from django import forms
from .models import Addresses


class AddressForm(forms.ModelForm):
    """Form to save addresses to registered users"""
    class Meta:
        model = Addresses
        exclude = ('user', 'email')

    def __init__(self, *args, **kwargs):
        """Provide initial address field details for the form"""
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
            'phone_nr': 'Phone Number'
        }
        self.fields['country'].widget.attrs['disabled'] = True
        for field in self.fields:
            if field != 'default_addr' and field != 'country':
                placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
                self.fields[field].widget.attrs['aria-label'] = placeholder

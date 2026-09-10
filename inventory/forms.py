from django import forms
from django.forms import ModelForm
from .models import Equipment

class EquipmentRequestForm(forms.Form):
    request_type = forms.ChoiceField(
        label="Request Type",
        choices=[
            ('', '-- Select Request Type --'),
            ('service', 'Service'),  
            ('repair', 'Repair'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_request_type'})
    )
    requester_name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Smith'})
    )
    requester_email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john.smith@pantonmcleod.co.uk'})
    )
    message = forms.CharField(
        label="Request Message",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please describe what you need this equipment for/any repairs that need to be done to the equipment, and any other relevant information.'
        })
    )


class EquipmentEditForm(ModelForm):

    LOCATION_CHOICES = [
        ('', '-- Select Location --'),
        ('Selkirk', 'Selkirk'),
        ('Wales', 'Wales'),
        ('SL26 BFO', 'SL26 BFO'),
        ('SL26 BCO', 'SL26 BCO'),
        ('SL26 BZJ', 'SL26 BZJ'),
        ('SL26 CXG', 'SL26 CXG'),
        ('SL26 CXF', 'SL26 CXF'),
        ('SL26 LWK', 'SL26 LWK'),
        ('SL26 KDO', 'SL26 KDO'),
        ('SL26 XZV', 'SL26 XZV'),
        ('SL26 CYF', 'SL26 CYF'),
        ('SL26 CYE', 'SL26 CYE'),
        ('SL26 CYJ', 'SL26 CYJ'),
        ('SL26 CXK', 'SL26 CXK'),
        ('Other', 'Other'),
    ]

    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Equipment
        fields = ['type', 'serial_number', 'location', 'purchase_date', 'last_service', 'next_service', 'notes']
        widgets = {
            'type':          forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_service':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_service':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SignInOutForm(forms.Form):
    LOCATION_CHOICES = [
        ('', '-- Select Location --'),
        ('Selkirk', 'Selkirk'),
        ('Wales', 'Wales'),
        ('SL26 BFO', 'SL26 BFO'),
        ('SL26 BCO', 'SL26 BCO'),
        ('SL26 BZJ', 'SL26 BZJ'),
        ('SL26 CXG', 'SL26 CXG'),
        ('SL26 CXF', 'SL26 CXF'),
        ('SL26 LWK', 'SL26 LWK'),
        ('SL26 KDO', 'SL26 KDO'),
        ('SL26 XZV', 'SL26 XZV'),
        ('SL26 CYF', 'SL26 CYF'),
        ('SL26 CYE', 'SL26 CYE'),
        ('SL26 CYJ', 'SL26 CYJ'),
        ('SL26 CXK', 'SL26 CXK'),
        ('Other', 'Other'),
    ]

    name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Smith'})
    )
    new_location = forms.ChoiceField(
        label="New Location",
        choices=LOCATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Select Excel File",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )
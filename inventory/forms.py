from django import forms

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
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please describe what you need this equipment for/any repairs that need to be done to the equipment, and any other relevant information.'
        })
    )

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
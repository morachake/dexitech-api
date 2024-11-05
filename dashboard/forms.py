from django import forms
from .models import ServiceProvider, ProviderDocument
from services.models import Service
import re

class ProviderForm(forms.ModelForm):
    services_offered = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=True
    )
    
    documentation = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        }),
        required=True
    )

    class Meta:
        model = ServiceProvider
        fields = [
            'provider_type', 'business_name', 'contact_email',
            'contact_phone', 'location', 'services_offered', 'notes'
        ]
        widgets = {
            'provider_type': forms.RadioSelect(attrs={'class': 'btn-check'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if not re.match(r'^\+?1?\d{9,15}$', phone):
            raise forms.ValidationError('Enter a valid phone number')
        return phone

    def clean_business_name(self):
        name = self.cleaned_data.get('business_name')
        if ServiceProvider.objects.filter(business_name__iexact=name).exists():
            raise forms.ValidationError('A provider with this business name already exists')
        return name

    def clean_documentation(self):
        files = self.files.getlist('documentation')
        if not files:
            raise forms.ValidationError('At least one document is required')
        
        for file in files:
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError(f'File {file.name} is too large. Maximum size is 5MB')
            
            # Check file type
            allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            if not any(file.name.lower().endswith(ext) for ext in allowed_types):
                raise forms.ValidationError(f'File {file.name} has an invalid type')
        
        return files
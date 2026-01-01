from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = [
            'name_of_resource',
            'resource_unit',
            'resource_group',
        ]

        labels = {
            'name_of_resource': 'Resource Name',
            'resource_unit': 'Resource Unit',
            'resource_group': 'Resource Group',
        }

        widgets = {
            'name_of_resource': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter resource name'
            }),
            'resource_unit': forms.Select(attrs={
                'class': 'form-control',
            }),
            'resource_group': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

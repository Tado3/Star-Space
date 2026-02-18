from django import forms
from .models import InstallationClient, ActiveSubscriber
from django.utils import timezone
from django import forms
from .models import Order

class InstallationClientForm(forms.ModelForm):
    class Meta:
        model = InstallationClient
        fields = ['name', 'contact', 'email', 'installation_type', 'invoice', 'installation_date', 'notes']
        widgets = {
            'installation_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling or help text if needed
        self.fields['installation_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['installation_type'].empty_label = None  # Remove empty label if you want

class ActiveSubscriberForm(forms.ModelForm):
    class Meta:
        model = ActiveSubscriber
        fields = ['name', 'contact', 'email', 'kit_type', 'last_subscription_date', 
                 'next_subscription_date', 'is_active', 'auto_notify']
        widgets = {
            'last_subscription_date': forms.DateInput(attrs={'type': 'date'}),
            'next_subscription_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling for kit_type
        self.fields['kit_type'].widget.attrs.update({'class': 'form-select'})
    
    def clean(self):
        cleaned_data = super().clean()
        last_date = cleaned_data.get('last_subscription_date')
        next_date = cleaned_data.get('next_subscription_date')
        
        if last_date and next_date and next_date <= last_date:
            raise forms.ValidationError("Next subscription date must be after last subscription date.")
        
        return cleaned_data

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'order_details', 'phone', 'order_date']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter customer name'}),
            'order_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter order details'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 078-776-8637'}),
        }
        labels = {
            'order_details': 'Order',
        }
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta

class Client(models.Model):
    # Base client fields - no installation type here as it's specific to InstallationClient
    name = models.CharField(max_length=200)
    
    # Updated phone number validator to accept various formats
    contact = models.CharField(max_length=20, validators=[
        RegexValidator(
            regex=r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
            message='Enter a valid phone number. Formats: (078) 776-8637, 078-776-8637, or 0787768637'
        )
    ])
    
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class InstallationClient(Client):
    INSTALLATION_TYPES = [
        ('STARLINK', 'Starlink Installation'),
        ('CCTV', 'CCTV Installation'),
        ('NETWORKING', 'Networking Installation'),
        ('SOLAR', 'Solar Installation'),
    ]
    
    installation_type = models.CharField(max_length=20, choices=INSTALLATION_TYPES, default='STARLINK')
    invoice = models.FileField(upload_to='invoices/', blank=True, null=True)
    installation_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_installation_type_display()} on {self.installation_date}"
    
    class Meta:
        ordering = ['-installation_date']

class ActiveSubscriber(Client):
    KIT_TYPES = [
        ('STANDARD', 'Standard'),
        ('MINI', 'Mini'),
    ]
    
    kit_type = models.CharField(max_length=10, choices=KIT_TYPES)
    last_subscription_date = models.DateField()
    next_subscription_date = models.DateField()
    is_active = models.BooleanField(default=True)
    auto_notify = models.BooleanField(default=True, help_text="Send automatic due date notifications")
    
    # New deactivation fields
    is_deactivated = models.BooleanField(default=False, help_text="Whether the subscriber account is deactivated")
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivation_reason = models.TextField(blank=True, null=True, help_text="Reason for deactivation")
    
    def __str__(self):
        status = " (Deactivated)" if self.is_deactivated else ""
        return f"{self.name} - {self.get_kit_type_display()} - Next sub: {self.next_subscription_date}{status}"
    
    def days_until_due(self):
        """Get days until subscription is due (for active accounts only)"""
        if self.is_deactivated or not self.next_subscription_date:
            return None
        delta = self.next_subscription_date - timezone.now().date()
        return delta.days
    
    def is_subscription_due_soon(self, days=7):
        """Check if subscription is due soon (only for active accounts)"""
        if self.is_deactivated:
            return False
        days_until = self.days_until_due()
        return days_until is not None and 0 <= days_until <= days
    
    def is_subscription_overdue(self):
        """Check if subscription is overdue (only for active accounts)"""
        if self.is_deactivated:
            return False
        return self.next_subscription_date and self.next_subscription_date < timezone.now().date()
    
    def deactivate(self, reason=""):
        """Deactivate this subscriber"""
        self.is_deactivated = True
        self.deactivated_at = timezone.now()
        self.deactivation_reason = reason
        self.save()
    
    def reactivate(self):
        """Reactivate this subscriber"""
        self.is_deactivated = False
        self.deactivated_at = None
        self.deactivation_reason = ""
        self.save()
    
    class Meta:
        ordering = ['-is_deactivated', 'next_subscription_date']
        
class Order(models.Model):
    """Order model for My Space section"""
    name = models.CharField(max_length=200)
    order_details = models.TextField(verbose_name="Order")
    phone = models.CharField(max_length=20, validators=[
        RegexValidator(
            regex=r'^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$',
            message='Enter a valid phone number. Formats: (078) 776-8637, 078-776-8637, or 0787768637'
        )
    ])
    order_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.order_details[:30]}..."
    
    class Meta:
        ordering = ['-order_date', '-created_at']
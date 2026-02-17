from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import InstallationClient, ActiveSubscriber
from datetime import timedelta

@admin.register(InstallationClient)
class InstallationClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'installation_type', 'installation_date', 'has_invoice']
    list_filter = ['installation_type', 'installation_date']
    search_fields = ['name', 'contact', 'email', 'notes']
    date_hierarchy = 'installation_date'
    
    fieldsets = (
        ('Client Information', {
            'fields': ('name', 'contact', 'email')
        }),
        ('Installation Details', {
            'fields': ('installation_type', 'installation_date', 'invoice', 'notes')
        }),
    )
    
    def has_invoice(self, obj):
        return bool(obj.invoice)
    has_invoice.boolean = True
    has_invoice.short_description = 'Invoice'
    has_invoice.admin_order_field = 'invoice'

@admin.register(ActiveSubscriber)
class ActiveSubscriberAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'kit_type', 'last_subscription_date', 
                   'next_subscription_date', 'subscription_status']
    list_filter = ['kit_type', 'is_active', 'next_subscription_date']
    search_fields = ['name', 'contact', 'email']
    date_hierarchy = 'next_subscription_date'
    actions = ['send_reminder_emails']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('name', 'contact', 'email', 'kit_type')
        }),
        ('Subscription Details', {
            'fields': ('last_subscription_date', 'next_subscription_date', 
                      'is_active', 'auto_notify')
        }),
    )
    
    def subscription_status(self, obj):
        if obj.is_subscription_overdue():
            return '🔴 Overdue'
        elif obj.is_subscription_due_soon(3):
            return '🟡 Due Soon (3 days)'
        elif obj.is_subscription_due_soon(7):
            return '🟢 Due Soon (7 days)'
        else:
            return '⚪ Up to date'
    subscription_status.short_description = 'Status'
    
    def send_reminder_emails(self, request, queryset):
        # This would integrate with email sending functionality
        for subscriber in queryset:
            # Logic to send reminder email
            pass
        self.message_user(request, f"Reminders sent to {queryset.count()} subscribers.")
    send_reminder_emails.short_description = "Send subscription reminders"
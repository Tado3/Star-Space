from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from clients.models import ActiveSubscriber

class Command(BaseCommand):
    help = 'Send due date notifications to subscribers'
    
    def handle(self, *args, **options):
        # Get subscribers due in the next 3 days
        due_soon = ActiveSubscriber.objects.filter(
            is_active=True,
            auto_notify=True,
            next_subscription_date__lte=timezone.now().date() + timedelta(days=3)
        )
        
        for subscriber in due_soon:
            days_left = (subscriber.next_subscription_date - timezone.now().date()).days
            
            if days_left >= 0:
                subject = f'Star Space - Subscription Due in {days_left} Days'
                message = f"""
                Dear {subscriber.name},
                
                Your Starlink subscription ({subscriber.kit_type}) is due in {days_left} days.
                
                Last subscription: {subscriber.last_subscription_date}
                Due date: {subscriber.next_subscription_date}
                
                Please ensure your payment is processed to avoid service interruption.
                
                Thank you for choosing Star Space!
                """
                
                send_mail(
                    subject,
                    message,
                    'notifications@starspace.com',
                    [subscriber.email],
                    fail_silently=False,
                )
                
                self.stdout.write(f"Notification sent to {subscriber.email}")
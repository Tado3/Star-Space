from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json
from .models import InstallationClient, ActiveSubscriber
from .forms import InstallationClientForm, ActiveSubscriberForm

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('clients:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('clients:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'clients/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('clients:login')

# Registration view
def register_view(request):
    if request.user.is_authenticated:
        return redirect('clients:dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('clients:dashboard')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    
    return render(request, 'clients/register.html', {'form': form})

# Add login required decorator to all protected views
@login_required(login_url='clients:login')
def dashboard(request):
    # Get statistics for dashboard
    total_installations = InstallationClient.objects.count()
    recent_installations = InstallationClient.objects.order_by('-installation_date')[:5]
    
    # Installation type statistics
    starlink_installations = InstallationClient.objects.filter(installation_type='STARLINK').count()
    cctv_installations = InstallationClient.objects.filter(installation_type='CCTV').count()
    networking_installations = InstallationClient.objects.filter(installation_type='NETWORKING').count()
    solar_installations = InstallationClient.objects.filter(installation_type='SOLAR').count()
    
    # Subscriber statistics - only count active (not deactivated) subscribers
    active_subscribers = ActiveSubscriber.objects.filter(is_deactivated=False)
    total_active = active_subscribers.count()
    
    due_soon = active_subscribers.filter(
        next_subscription_date__lte=timezone.now().date() + timedelta(days=7),
        next_subscription_date__gte=timezone.now().date()
    ).count()
    
    overdue = active_subscribers.filter(
        next_subscription_date__lt=timezone.now().date()
    ).count()
    
    # Deactivated count
    deactivated_count = ActiveSubscriber.objects.filter(is_deactivated=True).count()
    
    context = {
        'total_installations': total_installations,
        'recent_installations': recent_installations,
        'installation_stats': {
            'starlink': starlink_installations,
            'cctv': cctv_installations,
            'networking': networking_installations,
            'solar': solar_installations,
        },
        'total_active': total_active,
        'due_soon': due_soon,
        'overdue': overdue,
        'deactivated_count': deactivated_count,
        'kit_type_stats': {
            'standard': active_subscribers.filter(kit_type='STANDARD').count(),
            'mini': active_subscribers.filter(kit_type='MINI').count(),
        }
    }
    return render(request, 'clients/dashboard.html', context)

@login_required(login_url='clients:login')
def installation_list(request):
    installations = InstallationClient.objects.all()
    
    # Add counts for filtering if needed
    context = {
        'installations': installations,
        'starlink_count': installations.filter(installation_type='STARLINK').count(),
        'cctv_count': installations.filter(installation_type='CCTV').count(),
        'networking_count': installations.filter(installation_type='NETWORKING').count(),
        'solar_count': installations.filter(installation_type='SOLAR').count(),
    }
    return render(request, 'clients/installation_list.html', context)

@login_required(login_url='clients:login')
def add_installation(request):
    if request.method == 'POST':
        form = InstallationClientForm(request.POST, request.FILES)
        if form.is_valid():
            installation = form.save()
            messages.success(request, f'{installation.get_installation_type_display()} client added successfully!')
            return redirect('clients:installation_list')
    else:
        form = InstallationClientForm()
    return render(request, 'clients/installation_form.html', {'form': form, 'type': 'Installation'})

@login_required(login_url='clients:login')
def installation_detail(request, pk):
    installation = get_object_or_404(InstallationClient, pk=pk)
    return render(request, 'clients/installation_detail.html', {'installation': installation})

@login_required(login_url='clients:login')
def edit_installation(request, pk):
    installation = get_object_or_404(InstallationClient, pk=pk)
    if request.method == 'POST':
        form = InstallationClientForm(request.POST, request.FILES, instance=installation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Installation client updated successfully!')
            return redirect('clients:installation_detail', pk=installation.pk)
    else:
        form = InstallationClientForm(instance=installation)
    return render(request, 'clients/installation_form.html', {'form': form, 'type': 'Installation'})

@login_required(login_url='clients:login')
def subscriber_list(request):
    subscribers = ActiveSubscriber.objects.all()
    
    # Calculate counts
    total_count = subscribers.count()
    active_count = subscribers.filter(is_deactivated=False, next_subscription_date__gte=timezone.now().date()).count()
    due_soon_count = subscribers.filter(
        is_deactivated=False,
        next_subscription_date__lte=timezone.now().date() + timedelta(days=7),
        next_subscription_date__gte=timezone.now().date()
    ).count()
    overdue_count = subscribers.filter(
        is_deactivated=False,
        next_subscription_date__lt=timezone.now().date()
    ).count()
    deactivated_count = subscribers.filter(is_deactivated=True).count()
    
    context = {
        'subscribers': subscribers,
        'active_count': active_count,
        'due_soon_count': due_soon_count,
        'overdue_count': overdue_count,
        'deactivated_count': deactivated_count,
    }
    return render(request, 'clients/subscriber_list.html', context)

@login_required(login_url='clients:login')
def add_subscriber(request):
    if request.method == 'POST':
        form = ActiveSubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Active subscriber added successfully!')
            return redirect('clients:subscriber_list')
    else:
        form = ActiveSubscriberForm()
    return render(request, 'clients/subscriber_form.html', {'form': form, 'type': 'Subscriber'})

@login_required(login_url='clients:login')
def subscriber_detail(request, pk):
    subscriber = get_object_or_404(ActiveSubscriber, pk=pk)
    return render(request, 'clients/subscriber_detail.html', {'subscriber': subscriber})

@login_required(login_url='clients:login')
def edit_subscriber(request, pk):
    subscriber = get_object_or_404(ActiveSubscriber, pk=pk)
    if request.method == 'POST':
        form = ActiveSubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscriber updated successfully!')
            return redirect('clients:subscriber_detail', pk=subscriber.pk)
    else:
        form = ActiveSubscriberForm(instance=subscriber)
    return render(request, 'clients/subscriber_form.html', {'form': form, 'type': 'Subscriber'})

# Deactivation Views
@login_required(login_url='clients:login')
@require_POST
def deactivate_subscriber(request, pk):
    """Deactivate a subscriber"""
    try:
        subscriber = get_object_or_404(ActiveSubscriber, pk=pk)
        
        # Get reason from POST data if available
        data = json.loads(request.body) if request.body else {}
        reason = data.get('reason', '')
        
        subscriber.deactivate(reason)
        
        return JsonResponse({
            'success': True,
            'message': f'Subscriber {subscriber.name} deactivated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required(login_url='clients:login')
@require_POST
def reactivate_subscriber(request, pk):
    """Reactivate a subscriber"""
    try:
        subscriber = get_object_or_404(ActiveSubscriber, pk=pk)
        subscriber.reactivate()
        
        return JsonResponse({
            'success': True,
            'message': f'Subscriber {subscriber.name} reactivated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required(login_url='clients:login')
@require_POST
def bulk_deactivate_subscribers(request):
    """Bulk deactivate subscribers"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        reason = data.get('reason', 'Bulk deactivation')
        
        if not ids:
            return JsonResponse({
                'success': False,
                'error': 'No subscriber IDs provided'
            }, status=400)
        
        # Update all selected subscribers
        subscribers = ActiveSubscriber.objects.filter(pk__in=ids)
        count = 0
        
        for subscriber in subscribers:
            subscriber.deactivate(reason)
            count += 1
        
        return JsonResponse({
            'success': True,
            'count': count,
            'message': f'{count} subscribers deactivated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

# Payment processing for overdue/due soon subscribers
@login_required(login_url='clients:login')
def mark_subscriber_paid(request, pk):
    subscriber = get_object_or_404(ActiveSubscriber, pk=pk)
    
    if request.method == 'POST':
        # Get payment details from form
        payment_date = request.POST.get('payment_date')
        next_subscription_months = int(request.POST.get('next_subscription_months', 1))
        
        # Convert payment_date string to date object
        if payment_date:
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        else:
            payment_date = timezone.now().date()
        
        # Update subscription dates
        subscriber.last_subscription_date = payment_date
        subscriber.next_subscription_date = payment_date + timedelta(days=30 * next_subscription_months)
        subscriber.save()
        
        messages.success(request, f'Payment recorded for {subscriber.name}. Next subscription due: {subscriber.next_subscription_date.strftime("%d %b %Y")}')
        
        # Redirect back to the page they came from
        next_url = request.POST.get('next', 'clients:subscriber_list')
        return redirect(next_url)
    
    return render(request, 'clients/mark_paid.html', {'subscriber': subscriber})

# Bulk payment processing
@login_required(login_url='clients:login')
def bulk_mark_paid(request):
    if request.method == 'POST':
        # Get subscriber IDs - handle both list and comma-separated string
        subscriber_ids = request.POST.getlist('subscriber_ids')
        
        # If it's a single comma-separated string, split it
        if subscriber_ids and len(subscriber_ids) == 1 and ',' in subscriber_ids[0]:
            subscriber_ids = subscriber_ids[0].split(',')
        
        # Remove any empty strings
        subscriber_ids = [id for id in subscriber_ids if id]
        
        payment_date = request.POST.get('payment_date')
        next_subscription_months = int(request.POST.get('next_subscription_months', 1))
        
        # Convert payment_date string to date object
        if payment_date:
            payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        else:
            payment_date = timezone.now().date()
        
        if not subscriber_ids:
            messages.warning(request, 'No subscribers selected.')
            return redirect(request.POST.get('next', 'clients:subscriber_list'))
        
        subscribers = ActiveSubscriber.objects.filter(id__in=subscriber_ids, is_deactivated=False)
        count = 0
        
        for subscriber in subscribers:
            subscriber.last_subscription_date = payment_date
            # Calculate next subscription date correctly
            subscriber.next_subscription_date = payment_date + timedelta(days=30 * next_subscription_months)
            subscriber.save()
            count += 1
        
        messages.success(request, f'{count} subscriber(s) marked as paid successfully!')
        
        # Redirect back
        return redirect(request.POST.get('next', 'clients:subscriber_list'))
    
    return redirect('clients:subscriber_list')

@login_required(login_url='clients:login')
def subscribers_due_soon(request):
    due_soon = ActiveSubscriber.objects.filter(
        is_deactivated=False,
        next_subscription_date__lte=timezone.now().date() + timedelta(days=7),
        next_subscription_date__gte=timezone.now().date()
    ).order_by('next_subscription_date')
    
    # Add counts for standard and mini kits
    subscribers_standard_count = due_soon.filter(kit_type='STANDARD').count()
    subscribers_mini_count = due_soon.filter(kit_type='MINI').count()
    
    context = {
        'subscribers': due_soon,
        'subscribers_standard_count': subscribers_standard_count,
        'subscribers_mini_count': subscribers_mini_count,
    }
    return render(request, 'clients/due_soon.html', context)

@login_required(login_url='clients:login')
def subscribers_overdue(request):
    overdue = ActiveSubscriber.objects.filter(
        is_deactivated=False,
        next_subscription_date__lt=timezone.now().date()
    ).order_by('next_subscription_date')
    
    # Count by severity
    severe_count = overdue.filter(next_subscription_date__lte=timezone.now().date() - timedelta(days=30)).count()
    moderate_count = overdue.filter(
        next_subscription_date__gt=timezone.now().date() - timedelta(days=30),
        next_subscription_date__lte=timezone.now().date() - timedelta(days=15)
    ).count()
    mild_count = overdue.filter(next_subscription_date__gt=timezone.now().date() - timedelta(days=15)).count()
    
    # Kit type counts
    standard_count = overdue.filter(kit_type='STANDARD').count()
    mini_count = overdue.filter(kit_type='MINI').count()
    
    # Estimated revenue (assuming $100 per subscription)
    estimated_revenue = overdue.count() * 100
    
    context = {
        'subscribers': overdue,
        'subscribers_severe_count': severe_count,
        'subscribers_moderate_count': moderate_count,
        'subscribers_mild_count': mild_count,
        'subscribers_standard_count': standard_count,
        'subscribers_mini_count': mini_count,
        'estimated_revenue': estimated_revenue,
    }
    return render(request, 'clients/overdue.html', context)

# Optional: Filter installations by type
@login_required(login_url='clients:login')
def installations_by_type(request, installation_type):
    installations = InstallationClient.objects.filter(installation_type=installation_type.upper())
    type_display = dict(InstallationClient.INSTALLATION_TYPES).get(installation_type.upper(), installation_type)
    context = {
        'installations': installations,
        'installation_type': type_display,
    }
    return render(request, 'clients/installation_list.html', context)
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Main URLs
    path('', views.dashboard, name='dashboard'),
    
    # Installation URLs
    path('installations/', views.installation_list, name='installation_list'),
    path('installations/add/', views.add_installation, name='add_installation'),
    path('installations/<int:pk>/', views.installation_detail, name='installation_detail'),
    path('installations/<int:pk>/edit/', views.edit_installation, name='edit_installation'),
    path('installations/type/<str:installation_type>/', views.installations_by_type, name='installations_by_type'),
    
    # Subscriber URLs
    path('subscribers/', views.subscriber_list, name='subscriber_list'),
    path('subscribers/add/', views.add_subscriber, name='add_subscriber'),
    path('subscribers/<int:pk>/', views.subscriber_detail, name='subscriber_detail'),
    path('subscribers/<int:pk>/edit/', views.edit_subscriber, name='edit_subscriber'),
    path('subscribers/due-soon/', views.subscribers_due_soon, name='subscribers_due_soon'),
    path('subscribers/overdue/', views.subscribers_overdue, name='subscribers_overdue'),
    
    # Payment processing URLs
    path('subscribers/<int:pk>/mark-paid/', views.mark_subscriber_paid, name='mark_subscriber_paid'),
    path('subscribers/bulk-mark-paid/', views.bulk_mark_paid, name='bulk_mark_paid'),
    
    # Deactivation URLs
    path('subscribers/<int:pk>/deactivate/', views.deactivate_subscriber, name='deactivate_subscriber'),
    path('subscribers/<int:pk>/reactivate/', views.reactivate_subscriber, name='reactivate_subscriber'),
    path('subscribers/bulk-deactivate/', views.bulk_deactivate_subscribers, name='bulk_deactivate_subscribers'),
    
    # My Space URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.add_order, name='add_order'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/edit/', views.edit_order, name='edit_order'),
    path('orders/<int:pk>/delete/', views.delete_order, name='delete_order'),
]
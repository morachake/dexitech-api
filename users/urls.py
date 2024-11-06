from django.urls import path, include

urlpatterns = [
    # Client/User endpoints
    path('users/', include('api.users.urls')),
    
    # Service Provider endpoints
    path('providers/', include('api.providers.urls')),
    
    # Service endpoints
    path('services/', include('api.services.urls')),
    
    # Order endpoints
    path('orders/', include('api.orders.urls')),
    
    # Payment endpoints
    path('payments/', include('api.payments.urls')),
]
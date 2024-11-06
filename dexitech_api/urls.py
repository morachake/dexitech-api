from django.urls import path, include

urlpatterns = [
    # Mobile API endpoints
    path('client/', include('dexitech_api.users.urls')),
    # path('provider/', include('dexitech_api.providers.urls')),
    path('services/', include('dexitech_api.services.urls')),
    path('orders/', include('dexitech_api.orders.urls')),
    path('payments/', include('dexitech_api.payments.urls')),
]
from django.urls import path, include

urlpatterns = [
    path('auth/', include('api.auth.urls')),
    path('users/', include('api.users.urls')),
    path('providers/', include('api.providers.urls')),
    path('services/', include('api.services.urls')),
    path('requests/', include('api.requests.urls')),
]
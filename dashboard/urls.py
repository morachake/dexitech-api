from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router for dashboard
router = DefaultRouter()
router.register(r'providers', views.ServiceProviderViewSet)
router.register(r'documents', views.ProviderDocumentViewSet, basename='document')

# Dashboard URLs
urlpatterns = [
    # Dashboard views
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('providers/', views.ServiceProvidersView.as_view(), name='providers'),
    path('provider/<int:pk>/', views.ServiceProviderDetailView.as_view(), name='provider_detail'),
    path('requests/', views.ServiceRequestsView.as_view(), name='service_requests'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    
    # Dashboard API endpoints
    path('api/', include(router.urls)),
]
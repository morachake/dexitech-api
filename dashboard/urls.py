from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'providers', views.ServiceProviderViewSet)
router.register(r'requests', views.ServiceRequestViewSet)

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('providers/', views.ServiceProvidersView.as_view(), name='providers'),
    path('provider/<int:pk>/', views.ServiceProviderDetailView.as_view(), name='provider_detail'),
    path('requests/', views.ServiceRequestsView.as_view(), name='service_requests'),
    path('users/', views.UsersView.as_view(), name='users'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('api/', include(router.urls)),
]
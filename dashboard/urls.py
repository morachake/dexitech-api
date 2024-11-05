from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'providers', views.ServiceProviderViewSet)
router.register(r'requests', views.ServiceRequestViewSet)

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('api/', include(router.urls)),
]
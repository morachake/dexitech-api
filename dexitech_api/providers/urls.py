from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.ProviderRegistrationView.as_view(), name='provider-register'),
    path('auth/login/', views.ProviderLoginView.as_view(), name='provider-login'),
    
    # Profile Management
    path('profile/', views.ProviderProfileView.as_view(), name='provider-profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    
    # Documents
    path('documents/', views.DocumentUploadView.as_view(), name='upload-documents'),
    path('documents/<int:pk>/', views.DocumentDeleteView.as_view(), name='delete-document'),
    
    # Service Management
    path('services/', views.ProviderServicesView.as_view(), name='provider-services'),
    
    # Order Management
    path('orders/', views.ServiceRequestListView.as_view(), name='provider-requests'),
    path('orders/<int:pk>/', views.ServiceRequestDetailView.as_view(), name='request-detail'),
    path('orders/<int:pk>/accept/', views.AcceptRequestView.as_view(), name='accept-request'),
    path('orders/<int:pk>/reject/', views.RejectRequestView.as_view(), name='reject-request'),
    path('orders/<int:pk>/complete/', views.CompleteRequestView.as_view(), name='complete-request'),
    
    # Analytics
    path('analytics/', views.ProviderAnalyticsView.as_view(), name='provider-analytics'),
    path('earnings/', views.EarningsView.as_view(), name='provider-earnings'),
]
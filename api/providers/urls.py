from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.ProviderProfileView.as_view(), name='provider-profile'),
    path('services/', views.ProviderServicesView.as_view(), name='provider-services'),
    path('documents/', views.ProviderDocumentsView.as_view(), name='provider-documents'),
    path('verification-status/', views.VerificationStatusView.as_view(), name='verification-status'),
    path('requests/', views.ServiceRequestListView.as_view(), name='provider-requests'),
    path('requests/<int:pk>/', views.ServiceRequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:pk>/status/', views.UpdateRequestStatusView.as_view(), name='update-request-status'),
]
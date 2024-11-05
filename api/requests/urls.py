from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServiceRequestListCreateView.as_view(), name='request-list'),
    path('<int:pk>/', views.ServiceRequestDetailView.as_view(), name='request-detail'),
    path('<int:pk>/status/', views.UpdateRequestStatusView.as_view(), name='request-status'),
    path('history/', views.RequestHistoryView.as_view(), name='request-history'),
    path('<int:pk>/feedback/', views.FeedbackCreateView.as_view(), name='request-feedback'),
]
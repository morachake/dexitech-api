from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.InitiatePaymentView.as_view(), name='initiate-payment'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('callback/', views.MpesaCallbackView.as_view(), name='mpesa-callback'),
]
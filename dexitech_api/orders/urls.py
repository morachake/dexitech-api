from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateOrderView.as_view(), name='create-order'),
    path('list/', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/update/', views.UpdateOrderView.as_view(), name='update-order'),
    path('<int:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel-order'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.ClientRegistrationView.as_view(), name='client-register'),
    path('auth/login/', views.ClientLoginView.as_view(), name='client-login'),
    
    # Profile Management
    path('profile/', views.ClientProfileView.as_view(), name='client-profile'),
    path('profile/update/', views.ClientProfileUpdateView.as_view(), name='update-profile'),
    
    # Order Management
    path('orders/', views.ClientOrderListView.as_view(), name='client-orders'),
    path('orders/<int:pk>/', views.ClientOrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/cancel/', views.ClientOrderCancelView.as_view(), name='cancel-order'),
    
    # Reviews
    path('reviews/', views.ClientReviewListView.as_view(), name='client-reviews'),
    path('reviews/create/', views.CreateReviewView.as_view(), name='create-review'),
]
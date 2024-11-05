from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UpdateProfileView.as_view(), name='update-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
]
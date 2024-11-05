from django.urls import path
from . import views

urlpatterns = [
    path('', views.ServiceListCreateView.as_view(), name='service-list'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('categories/', views.ServiceCategoryListView.as_view(), name='service-categories'),
    path('search/', views.ServiceSearchView.as_view(), name='service-search'),
]
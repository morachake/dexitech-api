from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework import viewsets
from .models import ServiceProvider, ServiceRequest
from .serializers import ServiceProviderSerializer, ServiceRequestSerializer

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/index.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = ServiceProvider.objects.all()
        context['requests'] = ServiceRequest.objects.all()
        context['pending_requests'] = ServiceRequest.objects.filter(status='pending').count()
        context['active_providers'] = ServiceProvider.objects.filter(verification_status='approved').count()
        return context

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    
    def perform_update(self, serializer):
        instance = serializer.save()
        
class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    
    def get_queryset(self):
        queryset = ServiceRequest.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Avg, Sum
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ServiceProvider, ServiceRequest, ProviderReview, Client, ProviderDocument
from services.models import Service
from .serializers import ServiceProviderSerializer, ServiceRequestSerializer, ProviderReviewSerializer, ProviderDocumentSerializer
import json

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/index.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        
        # Basic counts
        context['providers'] = ServiceProvider.objects.all()
        context['requests'] = ServiceRequest.objects.all()
        context['active_providers'] = ServiceProvider.objects.filter(verification_status='approved').count()
        context['pending_requests'] = ServiceRequest.objects.filter(status='pending').count()
        context['user_count'] = User.objects.count()
        
        # Revenue calculation
        context['total_revenue'] = ServiceRequest.objects.filter(
            status='completed',
            created_at__gte=thirty_days_ago
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        return context

class ServiceProvidersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/providers.html'
    model = ServiceProvider
    context_object_name = 'providers'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.all()
        return context
    
    def get_queryset(self):
        queryset = ServiceProvider.objects.all()
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(business_name__icontains=search) |
                Q(contact_email__icontains=search)
            )
        if status:
            queryset = queryset.filter(verification_status=status)
            
        return queryset

class ServiceProviderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'dashboard/provider_detail.html'
    model = ServiceProvider
    context_object_name = 'provider'
    
    def test_func(self):
        return self.request.user.is_staff

class ServiceRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/requests.html'
    model = ServiceRequest
    context_object_name = 'requests'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_counts'] = {
            'pending': ServiceRequest.objects.filter(status='pending').count(),
            'in_progress': ServiceRequest.objects.filter(status='in_progress').count(),
            'completed': ServiceRequest.objects.filter(status='completed').count(),
            'disputed': ServiceRequest.objects.filter(status='disputed').count(),
        }
        return context

class UsersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/users.html'
    model = User
    context_object_name = 'users'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['new_users_today'] = User.objects.filter(
            date_joined__date=today.date()
        ).count()
        
        return context

class AnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/analytics.html'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now()
        thirty_days_ago = today - timedelta(days=30)
        
        # Revenue data for chart
        revenue_data = ServiceRequest.objects.filter(
            created_at__gte=thirty_days_ago
        ).values('created_at__date').annotate(
            total=Sum('amount')
        ).order_by('created_at__date')
        
        context['revenue_by_day'] = list(revenue_data)
        
        # Requests by status
        status_data = ServiceRequest.objects.values('status').annotate(
            count=Count('id')
        )
        context['requests_by_status'] = list(status_data)
        
        # User growth
        user_growth = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).values('date_joined__date').annotate(
            count=Count('id')
        ).order_by('date_joined__date')
        
        context['user_growth'] = list(user_growth)
        
        # Top providers
        context['top_providers'] = ServiceProvider.objects.filter(
            verification_status='approved'
        ).order_by('-average_rating')[:10]
        
        return context

class SettingsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'dashboard/settings.html'
    
    def test_func(self):
        return self.request.user.is_staff

class ServiceProviderViewSet(viewsets.ModelViewSet):
    queryset = ServiceProvider.objects.all()
    serializer_class = ServiceProviderSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            
            # Handle services offered
            services_offered = []
            if 'services_offered' in request.data:
                try:
                    services_offered = json.loads(request.data['services_offered'])
                except json.JSONDecodeError:
                    services_offered = request.data.getlist('services_offered')
            
            # Create provider
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            provider = serializer.save()
            
            # Add services
            if services_offered:
                provider.services_offered.set(services_offered)
            
            # Handle documents
            documents = request.FILES.getlist('documentation')
            for doc in documents:
                ProviderDocument.objects.create(
                    provider=provider,
                    name=doc.name,
                    file=doc,
                    document_type='identification'
                )
            
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            provider = self.get_object()
            data = request.data.copy()
            
            # Handle services offered
            services_offered = []
            if 'services_offered' in request.data:
                try:
                    services_offered = json.loads(request.data['services_offered'])
                except json.JSONDecodeError:
                    services_offered = request.data.getlist('services_offered')
            
            # Update provider
            serializer = self.get_serializer(provider, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            provider = serializer.save()
            
            # Update services
            if services_offered:
                provider.services_offered.set(services_offered)
            
            # Handle new documents
            documents = request.FILES.getlist('documentation')
            for doc in documents:
                ProviderDocument.objects.create(
                    provider=provider,
                    name=doc.name,
                    file=doc,
                    document_type='identification'
                )
            
            return Response({
                'status': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        try:
            provider = self.get_object()
            status_value = request.data.get('status')
            if status_value in ['approved', 'rejected']:
                provider.verification_status = status_value
                provider.save()
                return Response({'status': 'success'})
            return Response({
                'status': 'error',
                'message': 'Invalid status value'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ProviderDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = ProviderDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return ProviderDocument.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            document = self.get_object()
            document.delete()
            return Response({'status': 'success'})
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Avg, Sum
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ServiceProvider, ServiceRequest, ProviderReview, Client, ProviderDocument
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = ServiceProvider.objects.all()
        search_query = self.request.GET.get('search')
        status_filter = self.request.GET.get('status')
        
        if search_query:
            queryset = queryset.filter(
                Q(business_name__icontains=search_query) |
                Q(contact_email__icontains=search_query)
            )
        
        if status_filter:
            queryset = queryset.filter(verification_status=status_filter)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.values('id', 'name', 'description')
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context

class ServiceProviderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'dashboard/provider_detail.html'
    model = ServiceProvider
    context_object_name = 'provider'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Paginate service requests
        service_requests = self.object.servicerequest_set.all().order_by('-created_at')
        paginator = Paginator(service_requests, 10)
        page = self.request.GET.get('requests_page')
        
        try:
            context['service_requests'] = paginator.page(page)
        except PageNotAnInteger:
            context['service_requests'] = paginator.page(1)
        except EmptyPage:
            context['service_requests'] = paginator.page(paginator.num_pages)
            
        # Paginate reviews
        reviews = self.object.reviews.all().order_by('-created_at')
        review_paginator = Paginator(reviews, 5)
        review_page = self.request.GET.get('reviews_page')
        
        try:
            context['reviews'] = review_paginator.page(review_page)
        except PageNotAnInteger:
            context['reviews'] = review_paginator.page(1)
        except EmptyPage:
            context['reviews'] = review_paginator.page(review_paginator.num_pages)
            
        return context

class ServiceRequestsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/requests.html'
    model = ServiceRequest
    context_object_name = 'requests'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = ServiceRequest.objects.all()
        status_filter = self.request.GET.get('status')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_counts'] = {
            'pending': ServiceRequest.objects.filter(status='pending').count(),
            'in_progress': ServiceRequest.objects.filter(status='in_progress').count(),
            'completed': ServiceRequest.objects.filter(status='completed').count(),
            'disputed': ServiceRequest.objects.filter(status='disputed').count()
        }
        context['status_filter'] = self.request.GET.get('status', '')
        return context

class UsersView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'dashboard/users.html'
    model = User
    context_object_name = 'users'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = User.objects.all()
        search_query = self.request.GET.get('search')
        
        if search_query:
            queryset = queryset.filter(
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
            
        return queryset.order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['new_users_today'] = User.objects.filter(
            date_joined__date=timezone.now().date()
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

    def validate_phone_number(self, phone):
        # Basic phone validation - can be enhanced based on requirements
        pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not pattern.match(phone):
            raise ValidationError('Invalid phone number format')

    def validate_email(self, email):
        # Basic email validation
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not pattern.match(email):
            raise ValidationError('Invalid email format')

    def create(self, request, *args, **kwargs):
        try:
            # Validate required fields
            required_fields = ['business_name', 'contact_email', 'contact_phone', 'location', 'provider_type']
            for field in required_fields:
                if not request.data.get(field):
                    raise ValidationError(f'{field.replace("_", " ").title()} is required')

            # Validate email and phone
            self.validate_email(request.data['contact_email'])
            self.validate_phone_number(request.data['contact_phone'])

            # Validate services offered
            try:
                services_offered = json.loads(request.data.get('services_offered', '[]'))
                if not services_offered:
                    raise ValidationError('At least one service must be selected')
            except json.JSONDecodeError:
                raise ValidationError('Invalid services data')

            # Check if business name already exists
            if ServiceProvider.objects.filter(business_name__iexact=request.data['business_name']).exists():
                raise ValidationError('A provider with this business name already exists')

            # Create provider
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            provider = serializer.save()

            # Add services
            provider.services_offered.set(services_offered)

            # Handle documents
            documents = request.FILES.getlist('documentation')
            if not documents:
                raise ValidationError('At least one document is required')

            for doc in documents:
                # Validate file size (e.g., max 5MB)
                if doc.size > 5 * 1024 * 1024:
                    raise ValidationError('Document size should not exceed 5MB')
                
                # Validate file type
                allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
                if not any(doc.name.lower().endswith(ext) for ext in allowed_types):
                    raise ValidationError('Invalid document type')

                ProviderDocument.objects.create(
                    provider=provider,
                    name=doc.name,
                    file=doc,
                    document_type='identification'
                )

            return Response({
                'status': 'success',
                'message': 'Provider created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating the provider'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        try:
            provider = self.get_object()
            status_value = request.data.get('status')
            if status_value not in ['approved', 'rejected']:
                raise ValidationError('Invalid status value')

            provider.verification_status = status_value
            provider.save()
            return Response({
                'status': 'success',
                'message': f'Provider status updated to {status_value}'
            })
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
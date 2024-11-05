from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from dashboard.models import ServiceProvider, ServiceRequest, ProviderDocument
from .serializers import (
    ServiceProviderSerializer,
    ProviderServiceRequestSerializer,
    ProviderDocumentSerializer,
    ServicesOfferedSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProviderProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating provider profile"""
    serializer_class = ServiceProviderSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return get_object_or_404(ServiceProvider, user=self.request.user)

class ProviderServicesView(generics.RetrieveAPIView):
    """View for retrieving provider's offered services"""
    serializer_class = ServicesOfferedSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return get_object_or_404(ServiceProvider, user=self.request.user)

class ProviderDocumentsView(generics.ListCreateAPIView):
    """View for managing provider documents"""
    serializer_class = ProviderDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProviderDocument.objects.none()
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        return provider.documents.all()

    def perform_create(self, serializer):
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        serializer.save(provider=provider)

class ServiceRequestListView(generics.ListAPIView):
    """View for listing provider's service requests"""
    serializer_class = ProviderServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        return ServiceRequest.objects.filter(provider=provider)

class ServiceRequestDetailView(generics.RetrieveAPIView):
    """View for retrieving service request details"""
    serializer_class = ProviderServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        return ServiceRequest.objects.filter(provider=provider)

class UpdateRequestStatusView(generics.UpdateAPIView):
    """View for updating service request status"""
    permission_classes = [IsAuthenticated]
    serializer_class = ProviderServiceRequestSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        provider = get_object_or_404(ServiceProvider, user=self.request.user)
        return ServiceRequest.objects.filter(provider=provider)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['accepted', 'in_progress', 'completed', 'cancelled']
                )
            },
            required=['status']
        ),
        responses={
            200: openapi.Response('Status updated successfully'),
            400: 'Invalid status or transition',
            403: 'Not authorized',
            404: 'Request not found'
        }
    )
    def update(self, request, *args, **kwargs):
        provider = get_object_or_404(ServiceProvider, user=request.user)
        service_request = self.get_object()
        
        if service_request.provider != provider:
            return Response({
                'status': 'error',
                'message': 'Not authorized to update this request'
            }, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        valid_statuses = ['accepted', 'in_progress', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return Response({
                'status': 'error',
                'message': 'Invalid status. Must be one of: ' + ', '.join(valid_statuses)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not self._is_valid_status_transition(service_request.status, new_status):
            return Response({
                'status': 'error',
                'message': f'Invalid status transition from {service_request.status} to {new_status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        service_request.status = new_status
        service_request.save()
        
        return Response({
            'status': 'success',
            'message': 'Request status updated successfully'
        })

    def _is_valid_status_transition(self, current_status, new_status):
        valid_transitions = {
            'pending': ['accepted', 'cancelled'],
            'accepted': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': [],
            'disputed': []
        }
        return new_status in valid_transitions.get(current_status, [])

class VerificationStatusView(generics.RetrieveAPIView):
    """View for checking provider verification status"""
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceProviderSerializer

    def get_object(self):
        if getattr(self, 'swagger_fake_view', False):
            return None
        return get_object_or_404(ServiceProvider, user=self.request.user)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Verification status",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: 'Provider not found'
        }
    )
    def get(self, request, *args, **kwargs):
        provider = self.get_object()
        status_messages = {
            'pending': 'Your verification is pending review',
            'approved': 'Your account is verified',
            'rejected': 'Your verification was rejected'
        }
        return Response({
            'status': provider.verification_status,
            'message': status_messages.get(provider.verification_status, '')
        })
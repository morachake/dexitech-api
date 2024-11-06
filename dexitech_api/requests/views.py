from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from dashboard.models import ServiceRequest, ServiceProvider, ProviderReview
from .serializers import ClientServiceRequestSerializer, FeedbackSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ServiceRequestListCreateView(generics.ListCreateAPIView):
    """View for listing and creating service requests"""
    serializer_class = ClientServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        return ServiceRequest.objects.filter(client=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

class ServiceRequestDetailView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating service request details"""
    serializer_class = ClientServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        return ServiceRequest.objects.filter(client=self.request.user)

class UpdateRequestStatusView(generics.UpdateAPIView):
    """View for updating service request status"""
    permission_classes = [IsAuthenticated]
    serializer_class = ClientServiceRequestSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        return ServiceRequest.objects.filter(client=self.request.user)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['cancelled']
                )
            },
            required=['status']
        ),
        responses={
            200: openapi.Response('Status updated successfully'),
            400: 'Invalid status',
            404: 'Request not found'
        }
    )
    def update(self, request, *args, **kwargs):
        service_request = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['cancelled']:
            return Response({
                'status': 'error',
                'message': 'Clients can only cancel requests'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        service_request.status = new_status
        service_request.save()
        
        return Response({
            'status': 'success',
            'message': 'Request status updated successfully'
        })

class RequestHistoryView(generics.ListAPIView):
    """View for listing user's request history"""
    serializer_class = ClientServiceRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ServiceRequest.objects.none()
        return ServiceRequest.objects.filter(
            client=self.request.user
        ).order_by('-created_at')

class FeedbackCreateView(generics.CreateAPIView):
    """View for creating feedback for completed service requests"""
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    queryset = ProviderReview.objects.all()

    @swagger_auto_schema(
        request_body=FeedbackSerializer,
        responses={
            201: FeedbackSerializer(),
            400: 'Invalid data',
            404: 'Service request not found'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        request_obj = get_object_or_404(
            ServiceRequest,
            id=self.kwargs['pk'],
            client=self.request.user,
            status='completed'
        )
        serializer.save(
            user=self.request.user,
            provider=request_obj.provider
        )
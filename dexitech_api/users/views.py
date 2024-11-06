from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from .models import Client
from .serializers import (
    ClientRegistrationSerializer,
    ClientLoginSerializer,
    ClientProfileSerializer,
    ClientOrderSerializer,
    ClientReviewSerializer,
    ServiceListSerializer,
    ProviderListSerializer
)
from dexitech_api.orders.models import Order
from dexitech_api.providers.models import ServiceProvider, Review
from services.models import Service

class ClientRegistrationView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        
        return Response({
            'status': 'success',
            'message': 'Registration successful',
            'data': ClientProfileSerializer(client).data
        }, status=status.HTTP_201_CREATED)

class ClientLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ClientLoginSerializer

class ClientProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientProfileSerializer
    
    def get_object(self):
        return get_object_or_404(Client, user=self.request.user)

class ClientProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientProfileSerializer
    
    def get_object(self):
        return get_object_or_404(Client, user=self.request.user)

class ServiceListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceListSerializer
    queryset = Service.objects.all()
    
    def get_queryset(self):
        queryset = Service.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

class ServiceDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ServiceListSerializer
    queryset = Service.objects.all()

class ProviderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProviderListSerializer
    queryset = ServiceProvider.objects.filter(verification_status='approved')
    
    def get_queryset(self):
        queryset = ServiceProvider.objects.filter(verification_status='approved')
        service = self.request.query_params.get('service', None)
        if service:
            queryset = queryset.filter(services_offered=service)
        return queryset

class ProviderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProviderListSerializer
    queryset = ServiceProvider.objects.filter(verification_status='approved')

class ClientOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientOrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class ClientOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientOrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class ClientOrderUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientOrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status='pending'
        )

class ClientOrderCancelView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientOrderSerializer
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status__in=['pending', 'confirmed']
        )
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'status': 'success',
            'message': 'Order cancelled successfully'
        })

class ClientReviewListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientReviewSerializer
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

class CreateReviewView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClientReviewSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
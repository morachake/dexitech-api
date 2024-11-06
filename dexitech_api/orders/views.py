from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Order, OrderUpdate, Payment
from .serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer
)
import uuid

class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate order amount based on service price
        service = serializer.validated_data['service']
        amount = service.base_price  # You'll need to add base_price to Service model
        
        order = serializer.save(
            user=self.request.user,
            order_number=order_number,
            amount=amount,
            status='pending',
            payment_status='pending'
        )
        
        # Create initial order update
        OrderUpdate.objects.create(
            order=order,
            status='pending',
            comment='Order created successfully'
        )

class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class UpdateOrderView(generics.UpdateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status='pending'
        )
    
    def perform_update(self, serializer):
        order = serializer.save()
        OrderUpdate.objects.create(
            order=order,
            status=order.status,
            comment='Order details updated'
        )

class CancelOrderView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            status__in=['pending', 'confirmed']
        )
    
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        order.status = 'cancelled'
        order.save()
        
        OrderUpdate.objects.create(
            order=order,
            status='cancelled',
            comment='Order cancelled by user'
        )
        
        return Response({
            'status': 'success',
            'message': 'Order cancelled successfully'
        })
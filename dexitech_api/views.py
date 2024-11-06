from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Client
from .serializers import (
    ClientRegistrationSerializer,
    ClientProfileSerializer,
    ClientOrderSerializer
)
from dexitech_api.orders.models import Order

class ClientRegistrationView(generics.CreateAPIView):
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

class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Client, user=self.request.user)

class ClientOrderListView(generics.ListAPIView):
    serializer_class = ClientOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
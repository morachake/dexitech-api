from rest_framework import serializers
from .models import ServiceProvider, ServiceRequest, ProviderReview, Client
from services.serializers import ServiceSerializer

class ClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Client
        fields = ['id', 'username', 'email', 'client_type', 'business_name', 
                 'contact_person', 'location', 'created_at']

class ProviderReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ProviderReview
        fields = ['id', 'username', 'rating', 'comment', 'created_at']

class ServiceProviderSerializer(serializers.ModelSerializer):
    services_offered = ServiceSerializer(many=True, read_only=True)
    reviews = ProviderReviewSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceProvider
        fields = '__all__'

class ServiceRequestSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    client_name = serializers.CharField(source='client.user.username', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = ['id', 'client', 'client_name', 'provider', 'provider_name', 
                 'service_type', 'details', 'status', 'location', 'amount', 'created_at']
from rest_framework import serializers
from .models import ServiceProvider, ServiceRequest, ProviderReview, Client,ProviderDocument
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

class ProviderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDocument
        fields = ['id', 'name', 'file', 'document_type', 'uploaded_at']
        
class ServiceProviderSerializer(serializers.ModelSerializer):
    services_offered = ServiceSerializer(many=True, read_only=True)
    documents = ProviderDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'business_name', 'provider_type', 'verification_status',
            'contact_email', 'contact_phone', 'location', 'services_offered',
            'documents', 'notes', 'average_rating', 'total_reviews'
        ]
        read_only_fields = ['id', 'average_rating', 'total_reviews']

class ServiceRequestSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    client_name = serializers.CharField(source='client.user.username', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = ['id', 'client', 'client_name', 'provider', 'provider_name', 
                 'service_type', 'details', 'status', 'location', 'amount', 'created_at']
from rest_framework import serializers
from dashboard.models import ServiceProvider, ProviderDocument, ServiceRequest
from api.services.serializers import ServiceSerializer

class ProviderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDocument
        fields = ['id', 'name', 'file', 'document_type', 'uploaded_at']
        ref_name = 'APIProviderDocument'

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
        ref_name = 'APIServiceProvider'

class ProviderServiceRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'client_name', 'service_type', 'details', 'status',
            'location', 'amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        ref_name = 'APIProviderServiceRequest'

class ServicesOfferedSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(source='services_offered', many=True, read_only=True)
    
    class Meta:
        model = ServiceProvider
        fields = ['services']
        ref_name = 'APIServicesOffered'
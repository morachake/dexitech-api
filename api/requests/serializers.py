from rest_framework import serializers
from dashboard.models import ServiceRequest, ProviderReview
from api.providers.serializers import ServiceProviderSerializer

class ClientServiceRequestSerializer(serializers.ModelSerializer):
    provider_details = ServiceProviderSerializer(source='provider', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'provider', 'provider_details', 'client_name',
            'service_type', 'details', 'status', 'location',
            'amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        ref_name = 'ClientServiceRequest'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderReview
        fields = ['rating', 'comment']
        ref_name = 'ProviderReview'
        
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5"
            )
        return value
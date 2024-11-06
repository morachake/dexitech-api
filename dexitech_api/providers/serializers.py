from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ServiceProvider, ProviderDocument, Review
from dexitech_api.services.serializers import ServiceSerializer
from dexitech_api.orders.models import Order

class ProviderRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    provider_type = serializers.ChoiceField(choices=ServiceProvider.PROVIDER_TYPES)
    
    class Meta:
        model = ServiceProvider
        fields = [
            'provider_type', 'first_name', 'last_name', 'company_name',
            'registration_number', 'phone_number', 'address', 'city',
            'state', 'postal_code', 'bio', 'years_of_experience',
            'password'
        ]
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        
        provider = ServiceProvider.objects.create(user=user, **validated_data)
        return provider

class ProviderProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    services_offered = ServiceSerializer(many=True, read_only=True)
    documents = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'email', 'provider_type', 'verification_status',
            'first_name', 'last_name', 'company_name', 'registration_number',
            'phone_number', 'address', 'city', 'state', 'postal_code',
            'bio', 'years_of_experience', 'services_offered', 'documents',
            'average_rating', 'total_reviews', 'created_at'
        ]
        read_only_fields = ['id', 'verification_status', 'average_rating', 'total_reviews', 'created_at']
    
    def get_documents(self, obj):
        return ProviderDocumentSerializer(obj.documents.all(), many=True).data

class ProviderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDocument
        fields = [
            'id', 'document_type', 'title', 'file', 'expiry_date',
            'is_verified', 'uploaded_at'
        ]
        read_only_fields = ['id', 'is_verified', 'uploaded_at']

class ProviderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = ['services_offered']

class ProviderOrderSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='user.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'client_name', 'service_name', 'status',
            'amount', 'service_date', 'location', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProviderAnalyticsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    total_earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reviews = serializers.IntegerField()
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Client
from dexitech_api.orders.models import Order
from dexitech_api.providers.models import ServiceProvider, Review
from services.models import Service

class ClientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    client_type = serializers.ChoiceField(choices=Client.CLIENT_TYPES)
    
    class Meta:
        model = Client
        fields = [
            'client_type', 'first_name', 'last_name', 'company_name',
            'registration_number', 'phone_number', 'address', 'city',
            'state', 'postal_code', 'password'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        
        # Create User instance
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        
        # Create Client profile
        client = Client.objects.create(user=user, **validated_data)
        return client

class ClientLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Add user info to response
        data.update({
            'id': user.id,
            'email': user.email,
            'client_type': user.client_profile.client_type
        })
        
        return data

class ClientProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'email', 'client_type', 'first_name', 'last_name',
            'company_name', 'registration_number', 'phone_number',
            'address', 'city', 'state', 'postal_code', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ServiceListSerializer(serializers.ModelSerializer):
    provider_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'icon', 'provider_count']
    
    def get_provider_count(self, obj):
        return obj.providers.filter(verification_status='approved').count()

class ProviderListSerializer(serializers.ModelSerializer):
    services = ServiceListSerializer(source='services_offered', many=True)
    
    class Meta:
        model = ServiceProvider
        fields = [
            'id', 'company_name', 'provider_type', 'services',
            'city', 'state', 'average_rating', 'total_reviews'
        ]

class ClientOrderSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.company_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'provider_name', 'service_name',
            'status', 'payment_status', 'amount', 'service_date',
            'location', 'special_instructions', 'created_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'status', 'payment_status',
            'created_at'
        ]

class ClientReviewSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.company_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'provider', 'provider_name', 'rating',
            'comment', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
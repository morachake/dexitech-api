from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from dashboard.models import ServiceProvider, Client

class UserProfileSerializer(serializers.ModelSerializer):
    is_provider = serializers.SerializerMethodField()
    provider_profile = serializers.SerializerMethodField()
    client_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'is_provider', 'provider_profile', 'client_profile')
        read_only_fields = ('id', 'username', 'is_provider', 
                          'provider_profile', 'client_profile')

    def get_is_provider(self, obj):
        return hasattr(obj, 'serviceprovider')

    def get_provider_profile(self, obj):
        if hasattr(obj, 'serviceprovider'):
            provider = obj.serviceprovider
            return {
                'business_name': provider.business_name,
                'provider_type': provider.provider_type,
                'verification_status': provider.verification_status,
                'contact_email': provider.contact_email,
                'contact_phone': provider.contact_phone,
                'location': provider.location,
                'average_rating': provider.average_rating,
                'total_reviews': provider.total_reviews
            }
        return None

    def get_client_profile(self, obj):
        if hasattr(obj, 'client'):
            client = obj.client
            return {
                'client_type': client.client_type,
                'business_name': client.business_name,
                'contact_person': client.contact_person,
                'location': client.location
            }
        return None

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': ["The two password fields didn't match."]
            })
        return attrs
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from dashboard.models import ServiceProvider, Client

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    user_type = serializers.ChoiceField(choices=['client', 'provider'])
    business_type = serializers.ChoiceField(choices=['individual', 'entity'], required=False)
    business_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 
                 'last_name', 'user_type', 'business_type', 'business_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        if attrs['user_type'] == 'provider' and not attrs.get('business_type'):
            raise serializers.ValidationError({"business_type": "Business type is required for service providers."})
            
        return attrs

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        business_type = validated_data.pop('business_type', None)
        business_name = validated_data.pop('business_name', None)
        validated_data.pop('password2')
        
        user = User.objects.create_user(**validated_data)
        
        if user_type == 'provider':
            ServiceProvider.objects.create(
                user=user,
                provider_type=business_type,
                business_name=business_name or f"{user.first_name}'s Services"
            )
        else:
            Client.objects.create(
                user=user,
                client_type=business_type or 'individual',
                business_name=business_name
            )
        
        return user

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Add user type and profile info to response
        if hasattr(user, 'serviceprovider'):
            data['user_type'] = 'provider'
            data['profile'] = {
                'business_name': user.serviceprovider.business_name,
                'verification_status': user.serviceprovider.verification_status
            }
        elif hasattr(user, 'client'):
            data['user_type'] = 'client'
            data['profile'] = {
                'client_type': user.client.client_type,
                'business_name': user.client.business_name
            }
            
        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
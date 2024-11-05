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
    contact_phone = serializers.CharField(required=False)
    location = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 
                 'last_name', 'user_type', 'business_type', 'business_name',
                 'contact_phone', 'location')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Email uniqueness check
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email already exists."})
            
        # Validate provider-specific fields
        if attrs['user_type'] == 'provider':
            if not attrs.get('business_type'):
                raise serializers.ValidationError({"business_type": "Business type is required for service providers."})
            if not attrs.get('business_name'):
                raise serializers.ValidationError({"business_name": "Business name is required for service providers."})
            if not attrs.get('contact_phone'):
                raise serializers.ValidationError({"contact_phone": "Contact phone is required for service providers."})
            if not attrs.get('location'):
                raise serializers.ValidationError({"location": "Location is required for service providers."})
            
        return attrs

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        business_type = validated_data.pop('business_type', None)
        business_name = validated_data.pop('business_name', None)
        contact_phone = validated_data.pop('contact_phone', None)
        location = validated_data.pop('location', None)
        validated_data.pop('password2')
        
        password = validated_data.pop('password')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(password)
        user.save()
        
        if user_type == 'provider':
            ServiceProvider.objects.create(
                user=user,
                provider_type=business_type,
                business_name=business_name,
                contact_email=user.email,
                contact_phone=contact_phone,
                location=location
            )
        else:
            Client.objects.create(
                user=user,
                client_type=business_type or 'individual',
                business_name=business_name,
                location=location
            )
        
        return user

class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        
        # Add user info to response
        data.update({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
        
        # Add user type and profile info
        if hasattr(user, 'serviceprovider'):
            provider = user.serviceprovider
            data.update({
                'user_type': 'provider',
                'profile': {
                    'business_name': provider.business_name,
                    'provider_type': provider.provider_type,
                    'verification_status': provider.verification_status,
                    'contact_phone': provider.contact_phone,
                    'location': provider.location,
                    'average_rating': str(provider.average_rating),
                    'total_reviews': provider.total_reviews
                }
            })
        elif hasattr(user, 'client'):
            client = user.client
            data.update({
                'user_type': 'client',
                'profile': {
                    'client_type': client.client_type,
                    'business_name': client.business_name,
                    'location': client.location
                }
            })
            
        return data

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            # Don't reveal whether a user exists
            return value
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[validate_password])
    password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
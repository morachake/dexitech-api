from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'phone_number', 'address', 'created_at']
        ref_name= "AppUserProfile"
from rest_framework import serializers
from .models import Service

class ServiceSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'icon', 'icon_url', 'created_at']
        read_only_fields = ['id', 'created_at', 'icon_url']
    
    def get_icon_url(self, obj):
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
        return None
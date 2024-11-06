from rest_framework import serializers
from services.models import Service

class ServiceSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'icon', 'icon_url', 'created_at']
        read_only_fields = ['id', 'created_at', 'icon_url']
        ref_name = 'APIService'

    def get_icon_url(self, obj):
        if obj.icon and hasattr(obj.icon, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
        return None

    def validate_icon(self, value):
        if value:
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("File must be an image.")
            if value.size > 5 * 1024 * 1024:  # 5MB
                raise serializers.ValidationError("Image size cannot exceed 5MB.")
        return value

    def validate_name(self, value):
        # Case-insensitive unique validation
        if Service.objects.filter(name__iexact=value).exists():
            if not self.instance or self.instance.name.lower() != value.lower():
                raise serializers.ValidationError("A service with this name already exists.")
        return value
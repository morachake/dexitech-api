from rest_framework import serializers
from .models import Order, OrderUpdate, Payment
from dexitech_api.providers.models import ServiceProvider
from services.models import Service

class ServiceProviderBasicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceProvider
        fields = ['id', 'name', 'average_rating', 'total_reviews']
    
    def get_name(self, obj):
        if obj.provider_type == 'entity':
            return obj.company_name
        return f"{obj.first_name} {obj.last_name}"
    
class ServiceBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description']

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'provider', 'service', 'service_date', 'location',
            'special_instructions', 'contact_name', 'contact_phone',
            'contact_email'
        ]
    
    def validate_service_date(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Service date cannot be in the past")
        return value

class OrderDetailSerializer(serializers.ModelSerializer):
    provider = ServiceProviderBasicSerializer(read_only=True)
    service = ServiceBasicSerializer(read_only=True)
    updates = serializers.SerializerMethodField()
    payment_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = '__all__'
    
    def get_updates(self, obj):
        return OrderUpdateSerializer(obj.updates.all(), many=True).data
    
    def get_payment_info(self, obj):
        if hasattr(obj, 'payment'):
            return PaymentSerializer(obj.payment).data
        return None

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderUpdate
        fields = ['status', 'comment', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'amount', 'currency', 'status',
            'payment_method', 'created_at'
        ]

class OrderListSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.business_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'provider_name', 'service_name',
            'status', 'payment_status', 'amount', 'service_date',
            'created_at'
        ]
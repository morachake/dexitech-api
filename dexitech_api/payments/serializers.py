from rest_framework import serializers
from .models import MpesaPayment

class MpesaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaPayment
        fields = [
            'id', 'order', 'phone_number', 'amount', 'reference',
            'status', 'mpesa_receipt_number', 'created_at'
        ]
        read_only_fields = [
            'id', 'reference', 'status', 'mpesa_receipt_number',
            'created_at'
        ]

class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=15)

class PaymentStatusSerializer(serializers.Serializer):
    checkout_request_id = serializers.CharField()
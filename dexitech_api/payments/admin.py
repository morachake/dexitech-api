from django.contrib import admin
from .models import MpesaPayment

@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 'order', 'phone_number', 'amount',
        'status', 'mpesa_receipt_number', 'created_at'
    ]
    list_filter = ['status']
    search_fields = [
        'reference', 'checkout_request_id', 'mpesa_receipt_number',
        'order__order_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
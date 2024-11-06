from django.contrib import admin
from .models import Order, OrderUpdate, Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'provider', 'service', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status']
    search_fields = ['order_number', 'user__username', 'provider__business_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']

@admin.register(OrderUpdate)
class OrderUpdateAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['order__order_number']
    readonly_fields = ['created_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['payment_id', 'order__order_number']
    readonly_fields = ['created_at']
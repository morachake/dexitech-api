from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dexitech_api.orders'
    label = 'dexitech_orders'
    verbose_name = 'Dexitech Orders'
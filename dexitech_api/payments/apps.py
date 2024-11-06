from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dexitech_api.payments'
    label = 'dexitech_payments'
    verbose_name = 'Dexitech Payments'
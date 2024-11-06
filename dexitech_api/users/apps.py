from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dexitech_api.users'
    label = 'dexitech_users'
    verbose_name = 'Dexitech Users'
    
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Client

@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    """Create Client profile when a new user is created"""
    if created and not hasattr(instance, 'client_profile'):
        Client.objects.create(user=instance)
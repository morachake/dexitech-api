from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from dexitech_api.users.models import Client
from dexitech_api.providers.models import ServiceProvider

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create Client or Provider profile when a new user is created"""
    if created:
        if hasattr(instance, 'registration_type'):
            if instance.registration_type == 'client':
                Client.objects.create(user=instance)
            elif instance.registration_type == 'provider':
                ServiceProvider.objects.create(user=instance)

@receiver(post_save, sender=ServiceProvider)
def update_provider_rating(sender, instance, **kwargs):
    """Update provider rating when a new review is added"""
    reviews = instance.reviews.all()
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        instance.average_rating = total_rating / reviews.count()
        instance.total_reviews = reviews.count()
        instance.save()
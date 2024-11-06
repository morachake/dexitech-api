from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    CLIENT_TYPES = [
        ('individual', 'Individual'),
        ('entity', 'Entity')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, default='individual')
    
    # Individual fields
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    
    # Entity fields
    company_name = models.CharField(max_length=200, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Common fields
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'dexitech_users'

    def __str__(self):
        if self.client_type == 'entity':
            return f"{self.company_name} (Entity)"
        return f"{self.first_name} {self.last_name} (Individual)"
from django.db import models
from django.contrib.auth.models import User

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    documentation = models.FileField(upload_to='provider_docs/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.business_name

class ServiceRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True)
    service_type = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('assigned', 'Assigned'),
            ('completed', 'Completed'),
            ('disputed', 'Disputed')
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.service_type} - {self.status}"
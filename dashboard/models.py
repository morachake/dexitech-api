from django.db import models
from django.contrib.auth.models import User
from services.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator

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
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    services_offered = models.ManyToManyField(Service, related_name='providers', blank=True)
    documentation = models.FileField(upload_to='provider_docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    
    def __str__(self):
        return self.business_name
    
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews:
            total = sum(review.rating for review in reviews)
            self.average_rating = total / len(reviews)
            self.total_reviews = len(reviews)
            self.save()

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    client_type = models.CharField(
        max_length=20,
        choices=[
            ('individual', 'Individual'),
            ('entity', 'Entity')
        ],
        default='individual'
    )
    business_name = models.CharField(max_length=100, null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.client_type == 'entity':
            return f"{self.business_name} ({self.contact_person})"
        return self.user.get_full_name() or self.user.username

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed')
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='requests', null=True, blank=True)
    provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.CharField(max_length=50, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.service_type} - {self.status}"

class ProviderReview(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.provider.update_rating()
from django.db import models
from django.contrib.auth.models import User
from services.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator

class ServiceProvider(models.Model):
    PROVIDER_TYPES = [
        ('individual', 'Individual'),
        ('entity', 'Entity')
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES, default='individual')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    
    # Individual fields
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    
    # Entity fields
    company_name = models.CharField(max_length=200, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Common fields
    services_offered = models.ManyToManyField(Service, related_name='providers')
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    bio = models.TextField(null=True, blank=True)
    years_of_experience = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'dexitech_providers'

    def __str__(self):
        if self.provider_type == 'entity':
            return f"{self.company_name} (Entity)"
        return f"{self.first_name} {self.last_name} (Individual)"

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews:
            total = sum(review.rating for review in reviews)
            self.average_rating = total / len(reviews)
            self.total_reviews = len(reviews)
            self.save()

class ProviderDocument(models.Model):
    DOCUMENT_TYPES = [
        ('identification', 'Identification'),
        ('certification', 'Certification'),
        ('license', 'License'),
        ('insurance', 'Insurance'),
        ('other', 'Other')
    ]
    
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='provider_documents/')
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'dexitech_providers'

    def __str__(self):
        return f"{self.title} - {self.provider}"

class Review(models.Model):
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'dexitech_providers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review for {self.provider} by {self.user}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.provider.update_rating()
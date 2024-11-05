from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from services.models import Service
from dashboard.models import ServiceProvider, ProviderDocument, ServiceRequest
import random
from faker import Faker
import os
from pathlib import Path
import uuid

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            default=10,
            type=int,
            help='The number of users to create'
        )
        parser.add_argument(
            '--services',
            default=15,
            type=int,
            help='The number of services to create'
        )
        parser.add_argument(
            '--providers',
            default=20,
            type=int,
            help='The number of service providers to create'
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting data seeding...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created'))

        # Create regular users
        users = self._create_users(options['users'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} users'))

        # Create services
        services = self._create_services(options['services'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(services)} services'))

        # Create service providers
        providers = self._create_providers(options['providers'], services, users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(providers)} providers'))

        # Create service requests
        requests = self._create_requests(providers, users)
        self.stdout.write(self.style.SUCCESS(f'Created {len(requests)} service requests'))

        self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))

    def _generate_unique_username(self, prefix):
        """Generate a unique username with a given prefix"""
        while True:
            username = f'{prefix}_{uuid.uuid4().hex[:8]}'
            if not User.objects.filter(username=username).exists():
                return username

    def _create_users(self, count):
        users = []
        
        for _ in range(count):
            username = self._generate_unique_username('user')
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )
            users.append(user)
        
        return users

    def _create_services(self, count):
        services = []
        service_types = [
            'Plumbing', 'Electrical', 'Carpentry', 'Cleaning',
            'Painting', 'Gardening', 'Moving', 'Pest Control',
            'Appliance Repair', 'HVAC', 'Roofing', 'Flooring',
            'Window Cleaning', 'Pool Maintenance', 'Security System',
            'Solar Panel Installation', 'Interior Design', 'Landscaping',
            'Locksmith', 'Waste Removal'
        ]

        # Create a simple icon content
        icon_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\x00\x00szz\xf4\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x1atEXtSoftware\x00Paint.NET v3.5.100\xf4r\xa1\x00\x00\x00\x18IDAT8Oc\xf8\xff\xff?\x03)\x80\x89\x81D0j\xc0\xa8\x01\xa3\x06\x0c\x1b\x03\x00\x00\x00\xff\xff\x03\x00\x8d\xfc\x07\x81\x00\x00\x00\x00IEND\xaeB`\x82'

        for i in range(min(count, len(service_types))):
            name = service_types[i]
            # Check if service already exists
            if not Service.objects.filter(name=name).exists():
                icon = SimpleUploadedFile(
                    name=f'icon_{i}.png',
                    content=icon_content,
                    content_type='image/png'
                )
                
                service = Service.objects.create(
                    name=name,
                    description=fake.paragraph(),
                    icon=icon
                )
                services.append(service)

        return services

    def _create_providers(self, count, services, users):
        providers = []
        provider_types = ['individual', 'entity']
        verification_statuses = ['pending', 'approved', 'rejected']
        
        for _ in range(count):
            # Create a user for the provider
            username = self._generate_unique_username('provider')
            provider_user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )
            
            # Generate a unique business name
            while True:
                business_name = fake.company()
                if not ServiceProvider.objects.filter(business_name=business_name).exists():
                    break
            
            provider = ServiceProvider.objects.create(
                user=provider_user,
                business_name=business_name,
                provider_type=random.choice(provider_types),
                verification_status=random.choice(verification_statuses),
                contact_email=fake.email(),
                contact_phone=fake.phone_number(),
                location=fake.address(),
                notes=fake.text(),
                average_rating=random.uniform(3.0, 5.0),
                total_reviews=random.randint(0, 50)
            )
            
            # Assign random services (2-5 services per provider)
            selected_services = random.sample(list(services), random.randint(2, min(5, len(services))))
            provider.services_offered.set(selected_services)
            
            # Create sample documents
            for j in range(random.randint(1, 3)):
                doc_content = b'Sample document content'
                doc = SimpleUploadedFile(
                    name=f'doc_{uuid.uuid4().hex[:8]}.pdf',
                    content=doc_content,
                    content_type='application/pdf'
                )
                
                ProviderDocument.objects.create(
                    provider=provider,
                    name=f'Document {j+1}',
                    file=doc,
                    document_type='identification'
                )
            
            providers.append(provider)
        
        return providers

    def _create_requests(self, providers, users):
        requests = []
        statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled', 'disputed']
        
        # Create 2-5 requests per provider
        for provider in providers:
            for _ in range(random.randint(2, 5)):
                request = ServiceRequest.objects.create(
                    provider=provider,
                    client=random.choice(users),
                    service_type=random.choice(list(provider.services_offered.all())).name,
                    status=random.choice(statuses),
                    details=fake.paragraph(),
                    location=fake.address(),
                    amount=random.uniform(50.0, 500.0),
                    created_at=fake.date_time_between(
                        start_date='-1y',
                        end_date='now',
                        tzinfo=timezone.get_current_timezone()
                    )
                )
                requests.append(request)
        
        return requests
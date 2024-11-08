# Generated by Django 5.1.3 on 2024-11-05 15:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_remove_serviceprovider_documentation_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serviceprovider',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='servicerequest',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='business_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='service_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]

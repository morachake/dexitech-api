# Generated by Django 5.1.3 on 2024-11-05 12:13

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_serviceprovider_average_rating_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicerequest',
            name='user',
        ),
        migrations.AddField(
            model_name='serviceprovider',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='details',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='location',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='providerreview',
            name='rating',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='provider',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.serviceprovider'),
        ),
        migrations.AlterField(
            model_name='servicerequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('disputed', 'Disputed')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_type', models.CharField(choices=[('individual', 'Individual'), ('entity', 'Entity')], default='individual', max_length=20)),
                ('business_name', models.CharField(blank=True, max_length=100, null=True)),
                ('contact_person', models.CharField(blank=True, max_length=100, null=True)),
                ('location', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='servicerequest',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='dashboard.client'),
        ),
    ]

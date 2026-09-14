from django.db import models

from apps.users.models import User


class Institution(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='institution')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='institution_logos/', blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    opening_hours = models.TimeField(null=True, blank=True)
    closing_hours = models.TimeField(null=True, blank=True)
    working_days = models.JSONField(default=list, blank=True)
    is_currently_open = models.BooleanField(default=False)

    def __str__(self):
        return self.name

from django.db import models
from apps.users.models import User

class Institution(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='institution')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # ex: "Banque", "Poste"
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)  # ex: "Ouverture de compte"
    average_duration_minutes = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.institution.name}"
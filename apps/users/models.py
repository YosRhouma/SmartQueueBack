from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        CITIZEN = 'citizen', 'Citoyen'
        INSTITUTION = 'institution', 'Institution'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CITIZEN)
    phone = models.CharField(max_length=20, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='smartqueue_users',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='smartqueue_users_permissions',
        blank=True,
    )

    def __str__(self):
        return self.username


class CitizenProfile(models.Model):
    """Personal information kept separately from authentication data."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen_profile')
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    cin = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=30)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    governorate = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

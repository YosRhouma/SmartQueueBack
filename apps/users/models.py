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
from django.db import models
from apps.users.models import User
from apps.institutions.models import Service

class Ticket(models.Model):
    class Status(models.TextChoices):
        WAITING = 'waiting', 'En attente'
        CALLED = 'called', 'Appelé'
        SERVED = 'served', 'Servi'
        CANCELLED = 'cancelled', 'Annulé'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='tickets')
    number = models.PositiveIntegerField()  # ex: 42 (le "A042" affiché à l'utilisateur)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Ticket #{self.number} - {self.service.name}"
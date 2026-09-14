from django.db import models
from django.db.models import Q
from django.utils import timezone
from apps.users.models import User
from apps.institutions.models import Institution

class Ticket(models.Model):
    class Status(models.TextChoices):
        WAITING = 'waiting', 'En attente'
        CALLED = 'called', 'Appelé'
        SERVED = 'served', 'Servi'
        CANCELLED = 'cancelled', 'Annulé'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='tickets')
    number = models.PositiveIntegerField()  # ex: 42 (le "A042" affiché à l'utilisateur)
    # Each institution has one queue that restarts every day.
    queue_date = models.DateField(default=timezone.localdate, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    served_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            # A displayed number cannot be assigned twice in the same institution queue.
            models.UniqueConstraint(fields=['institution', 'queue_date', 'number'], name='unique_daily_institution_ticket_number'),
            # The “my current ticket” endpoint stays unambiguous for each citizen.
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(status__in=['waiting', 'called']),
                name='one_active_ticket_per_user',
            ),
        ]

    def __str__(self):
        return f"Ticket #{self.number} - {self.institution.name}"

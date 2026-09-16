from django.db import models
from apps.users.models import User


class Notification(models.Model):
    class Kind(models.TextChoices):
        GENERAL = 'general', 'General'
        ONE_BEFORE = 'one_before', 'One ticket before'
        TURN = 'turn', 'Turn'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    ticket = models.ForeignKey(
        'tickets.Ticket', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True,
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.GENERAL)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['ticket', 'kind'],
                condition=models.Q(ticket__isnull=False),
                name='unique_ticket_notification_kind',
            ),
        ]

    def __str__(self):
        return self.message
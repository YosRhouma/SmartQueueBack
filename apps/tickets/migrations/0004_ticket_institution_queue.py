# Generated for the institution-only queue workflow.
from django.db import migrations, models
import django.db.models.deletion


def move_tickets_to_institutions(apps, schema_editor):
    """Keep historic tickets while merging former service queues into their institution queue."""
    Ticket = apps.get_model('tickets', 'Ticket')

    tickets = list(Ticket.objects.select_related('service').order_by('created_at', 'pk'))
    active_users = set()
    next_numbers = {}
    for ticket in tickets:
        ticket.institution_id = ticket.service.institution_id

        # One citizen can retain only one active ticket after queues are merged.
        active_key = (ticket.user_id, ticket.queue_date)
        if ticket.status in ('waiting', 'called') and active_key in active_users:
            ticket.status = 'cancelled'
        elif ticket.status in ('waiting', 'called'):
            active_users.add(active_key)

        # Different service numbers may collide; assign a coherent historic institution sequence.
        queue_key = (ticket.institution_id, ticket.queue_date)
        next_numbers[queue_key] = next_numbers.get(queue_key, 0) + 1
        ticket.number = next_numbers[queue_key]
        ticket.save(update_fields=['institution', 'number', 'status'])


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0004_alter_institution_logo'),
        ('tickets', '0003_ticket_queue_date_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ticket',
            name='unique_daily_service_ticket_number',
        ),
        migrations.AddField(
            model_name='ticket',
            name='institution',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='institutions.institution'),
        ),
        migrations.RunPython(move_tickets_to_institutions, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='ticket',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='institutions.institution'),
        ),
        migrations.RemoveField(
            model_name='ticket',
            name='service',
        ),
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(fields=('institution', 'queue_date', 'number'), name='unique_daily_institution_ticket_number'),
        ),
    ]

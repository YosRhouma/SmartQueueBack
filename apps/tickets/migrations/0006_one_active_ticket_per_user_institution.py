from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_remove_one_active_ticket_per_user'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ticket',
            constraint=models.UniqueConstraint(
                fields=('user', 'institution'),
                condition=Q(status__in=['waiting', 'called']),
                name='one_active_ticket_per_user_institution',
            ),
        ),
    ]

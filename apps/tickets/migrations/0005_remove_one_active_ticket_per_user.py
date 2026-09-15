from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_ticket_institution_queue'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ticket',
            name='one_active_ticket_per_user',
        ),
    ]

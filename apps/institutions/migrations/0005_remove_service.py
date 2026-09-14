# Service queues were replaced by one queue directly owned by each institution.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_ticket_institution_queue'),
        ('institutions', '0004_alter_institution_logo'),
    ]

    operations = [
        migrations.DeleteModel(name='Service'),
    ]

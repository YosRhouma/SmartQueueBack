from rest_framework import serializers

from apps.institutions.models import Institution
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """Ticket data returned to its citizen, including live queue progress."""
    institution_id = serializers.IntegerField(source='institution.id', read_only=True)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    people_ahead = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ('id', 'institution_id', 'institution_name', 'number', 'status', 'queue_date',
                  'created_at', 'called_at', 'served_at', 'people_ahead')

    def get_people_ahead(self, ticket):
        # Only waiting tickets with a lower number remain ahead of this ticket.
        if ticket.status != Ticket.Status.WAITING:
            return 0
        return Ticket.objects.filter(
            institution=ticket.institution,
            queue_date=ticket.queue_date,
            status=Ticket.Status.WAITING,
            number__lt=ticket.number,
        ).count()


class TicketCreateSerializer(serializers.Serializer):
    """The citizen selects an institution; it owns the only queue."""
    institution_id = serializers.PrimaryKeyRelatedField(source='institution', queryset=Institution.objects.all())

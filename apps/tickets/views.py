from django.db import IntegrityError, transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from apps.institutions.models import Institution
from apps.notifications.models import Notification
from apps.notifications.services import broadcast_notification
from apps.users.models import User
from .models import Ticket
from .serializers import TicketCreateSerializer, TicketSerializer


class CitizenTicketPermission(permissions.BasePermission):
    """Only citizen accounts may reserve and view their own tickets."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.CITIZEN)


class InstitutionQueuePermission(permissions.BasePermission):
    """Only an institution owner may progress that institution's queue."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.INSTITUTION)


class TicketCreateAPIView(APIView):
    """Assign the next daily number in an institution's queue."""
    permission_classes = [CitizenTicketPermission]

    @swagger_auto_schema(
        tags=['Tickets'],
        operation_description='Reserve the next available ticket number for an institution.',
        request_body=TicketCreateSerializer,
        responses={201: TicketSerializer, 400: 'Invalid or inactive institution.'},
    )
    def post(self, request):
        serializer = TicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institution = serializer.validated_data['institution']
        if not institution.is_active:
            return Response({'detail': 'This institution is currently unavailable.'}, status=status.HTTP_400_BAD_REQUEST)

        queue_date = timezone.localdate()
        try:
            # Locking the institution serializes concurrent ticket-number allocation.
            with transaction.atomic():
                institution = Institution.objects.select_for_update().get(pk=institution.pk)
                last_number = Ticket.objects.filter(institution=institution, queue_date=queue_date).aggregate(Max('number'))['number__max'] or 0
                ticket = Ticket.objects.create(
                    user=request.user, institution=institution, queue_date=queue_date, number=last_number + 1,
                )
        except IntegrityError:
            # Database constraints protect the per-institution rule during concurrent requests.
            return Response({'detail': 'You already have an active ticket in this institution.'}, status=status.HTTP_409_CONFLICT)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


class CurrentTicketAPIView(APIView):
    """Return the citizen's single current ticket with the live number ahead."""
    permission_classes = [CitizenTicketPermission]

    @swagger_auto_schema(tags=['Tickets'], operation_description='Return the authenticated citizen\'s active ticket.')
    def get(self, request):
        ticket = Ticket.objects.filter(
            user=request.user, status__in=[Ticket.Status.WAITING, Ticket.Status.CALLED],
        ).select_related('institution').first()
        if ticket is None:
            return Response({'detail': 'No active ticket found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TicketSerializer(ticket).data)


class UserTicketsAPIView(APIView):
    """Return every ticket owned by the authenticated citizen."""
    permission_classes = [CitizenTicketPermission]

    @swagger_auto_schema(tags=['Tickets'], operation_description='Return all tickets owned by the authenticated citizen.')
    def get(self, request):
        tickets = Ticket.objects.filter(user=request.user).select_related('institution')
        return Response(TicketSerializer(tickets, many=True).data)


class TicketDetailAPIView(APIView):
    """A citizen cannot inspect another citizen's ticket by guessing its id."""
    permission_classes = [CitizenTicketPermission]

    @swagger_auto_schema(tags=['Tickets'], operation_description='Return one ticket owned by the authenticated citizen.')
    def get(self, request, pk):
        try:
            ticket = Ticket.objects.select_related('institution').get(pk=pk, user=request.user)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TicketSerializer(ticket).data)

    @swagger_auto_schema(tags=['Tickets'], operation_description='Cancel a waiting ticket owned by the authenticated citizen.')
    def delete(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk, user=request.user)
        except Ticket.DoesNotExist:
            return Response({'detail': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        if ticket.status != Ticket.Status.WAITING:
            return Response({'detail': 'Only a waiting ticket can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = Ticket.Status.CANCELLED
        ticket.save(update_fields=['status'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstitutionQueueAPIView(APIView):
    """Expose the current number and the end of one institution's queue."""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(tags=['Institutions'], operation_description='Return the current number and progress of an institution queue.')
    def get(self, request, pk):
        try:
            institution = Institution.objects.get(pk=pk, is_active=True)
        except Institution.DoesNotExist:
            return Response({'detail': 'Institution not found.'}, status=status.HTTP_404_NOT_FOUND)

        queue = Ticket.objects.filter(institution=institution, queue_date=timezone.localdate())
        current_ticket = queue.filter(status=Ticket.Status.CALLED).order_by('-called_at').first()
        last_number = queue.aggregate(Max('number'))['number__max'] or 0
        return Response({
            'institution_id': institution.id,
            'institution_name': institution.name,
            # Zero means that the institution has not called a number yet today.
            'current_number': current_ticket.number if current_ticket else 0,
            'last_ticket_number': last_number,
            'waiting_count': queue.filter(status=Ticket.Status.WAITING).count(),
            # The frontend can warn citizens before they reserve at a closed institution.
            'is_currently_open': institution.is_currently_open,
        })


class CallNextTicketAPIView(APIView):
    """Mark the previously called ticket as served, then call the next waiting number."""
    permission_classes = [InstitutionQueuePermission]

    @swagger_auto_schema(tags=['Institutions'], operation_description='Call the next waiting number for the authenticated institution.')
    def post(self, request):
        try:
            # The OneToOne relation ensures an institution owner can advance only their own queue.
            institution = request.user.institution
        except Institution.DoesNotExist:
            return Response({'detail': 'Institution profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not institution.is_active:
            return Response({'detail': 'This institution is currently unavailable.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            institution = Institution.objects.select_for_update().get(pk=institution.pk)
            queue = Ticket.objects.filter(institution=institution, queue_date=timezone.localdate())
            now = timezone.now()
            # Calling a new number completes the one that was being served.
            queue.filter(status=Ticket.Status.CALLED).update(status=Ticket.Status.SERVED, served_at=now)
            next_ticket = queue.filter(status=Ticket.Status.WAITING).order_by('number').first()
            if next_ticket is None:
                served_ticket = queue.filter(status=Ticket.Status.SERVED, served_at=now).order_by('-served_at').first()
                if served_ticket is None:
                    return Response({'detail': 'No ticket in the queue.'}, status=status.HTTP_404_NOT_FOUND)
                return Response(TicketSerializer(served_ticket).data)
            next_ticket.status = Ticket.Status.CALLED
            next_ticket.called_at = now
            next_ticket.save(update_fields=['status', 'called_at'])
            turn_notification, turn_created = Notification.objects.get_or_create(
                ticket=next_ticket,
                kind=Notification.Kind.TURN,
                defaults={
                    'user': next_ticket.user,
                    'message': f'C\'est votre tour à {next_ticket.institution.name}.',
                },
            )
            if turn_created:
                broadcast_notification(turn_notification)
            next_waiting_ticket = queue.filter(
                status=Ticket.Status.WAITING, number__gt=next_ticket.number,
            ).order_by('number').first()
            if next_waiting_ticket is not None:
                one_before_notification, one_before_created = Notification.objects.get_or_create(
                    ticket=next_waiting_ticket,
                    kind=Notification.Kind.ONE_BEFORE,
                    defaults={
                        'user': next_waiting_ticket.user,
                        'message': f'Il reste un ticket avant votre tour à {next_waiting_ticket.institution.name}.',
                    },
                )
                if one_before_created:
                    broadcast_notification(one_before_notification)
        return Response(TicketSerializer(next_ticket).data)

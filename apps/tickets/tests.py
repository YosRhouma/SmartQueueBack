from rest_framework import status
from rest_framework.test import APITestCase

from apps.institutions.models import Institution
from apps.users.models import User
from .models import Ticket


class InstitutionQueueAPITest(APITestCase):
    def setUp(self):
        # Every test starts with one institution and two distinct citizens.
        self.owner = User.objects.create_user(username='bank-owner', password='StrongPass123', role=User.Role.INSTITUTION)
        self.institution = Institution.objects.create(
            owner=self.owner, name='Banque Centrale', category='Banque', address='1 Rue de la Banque', city='Tunis',
        )
        self.first_citizen = User.objects.create_user(username='citizen-one', password='StrongPass123', role=User.Role.CITIZEN)
        self.second_citizen = User.objects.create_user(username='citizen-two', password='StrongPass123', role=User.Role.CITIZEN)

    def reserve_ticket(self, citizen):
        self.client.force_authenticate(citizen)
        return self.client.post('/api/tickets/', {'institution_id': self.institution.id}, format='json')

    def test_citizens_receive_consecutive_numbers_for_the_same_institution(self):
        # The institution queue—not a service—determines ticket numbers.
        first = self.reserve_ticket(self.first_citizen)
        second = self.reserve_ticket(self.second_citizen)

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first.data['number'], 1)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.data['number'], 2)

    def test_owner_calls_the_next_number_and_advances_the_queue(self):
        # Calling the next number serves the former current number automatically.
        first = self.reserve_ticket(self.first_citizen)
        second = self.reserve_ticket(self.second_citizen)
        self.client.force_authenticate(self.owner)

        first_call = self.client.post('/api/institutions/queue/next/')
        queue_after_first_call = self.client.get(f'/api/institutions/{self.institution.id}/queue/')
        second_call = self.client.post('/api/institutions/queue/next/')

        self.assertEqual(first_call.status_code, status.HTTP_200_OK)
        self.assertEqual(first_call.data['number'], first.data['number'])
        self.assertEqual(queue_after_first_call.data['current_number'], 1)
        self.assertEqual(queue_after_first_call.data['last_ticket_number'], 2)
        self.assertEqual(queue_after_first_call.data['waiting_count'], 1)
        self.assertEqual(second_call.data['number'], second.data['number'])
        self.assertEqual(Ticket.objects.get(pk=first.data['id']).status, Ticket.Status.SERVED)

    def test_current_ticket_reports_people_ahead_and_is_private(self):
        # A citizen sees progress for their own ticket but cannot read another ticket id.
        first = self.reserve_ticket(self.first_citizen)
        second = self.reserve_ticket(self.second_citizen)
        current = self.client.get('/api/tickets/my-current/')
        private_ticket = self.client.get(f'/api/tickets/{first.data["id"]}/')

        self.assertEqual(current.status_code, status.HTTP_200_OK)
        self.assertEqual(current.data['id'], second.data['id'])
        self.assertEqual(current.data['people_ahead'], 1)
        self.assertEqual(private_ticket.status_code, status.HTTP_404_NOT_FOUND)

import json

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from apps.institutions.models import Institution


class InstitutionProfileAPITest(APITestCase):
    def test_institution_can_create_profile(self):
        user = User.objects.create_user(
            username='institution', password='StrongPass123', role=User.Role.INSTITUTION,
        )
        self.client.force_authenticate(user=user)

        response = self.client.post('/api/institutions/profile/', {
            'officialName': 'Municipality of Tunis',
            'description': 'Public administration services.',
            'logo': SimpleUploadedFile(
                'logo.png',
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0dIDATx\x9cc\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82',
                content_type='image/png',
            ),
            'sector': 'Public service',
            'website': 'https://example.com',
            'email': 'contact@example.com',
            'phone': '+21671000000',
            'Localisation': json.dumps({
                'governorate': 'Tunis', 'address': '1 City Hall Road', 'postalCode': '1000',
            }),
            'Horaire': json.dumps({
                'openingHours': '08:00:00', 'closingHours': '16:00:00',
                'workingDays': ['monday', 'tuesday'], 'isCurrentlyOpen': True,
            }),
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['Horaire']['workingDays'], ['monday', 'tuesday'])

    def test_institution_can_delete_own_profile(self):
        user = User.objects.create_user(
            username='institution', password='StrongPass123', role=User.Role.INSTITUTION,
        )
        Institution.objects.create(
            owner=user, name='Municipality of Tunis', category='Public service', city='Tunis',
            address='1 City Hall Road', postal_code='1000', opening_hours='08:00:00',
            closing_hours='16:00:00', working_days=['monday'], is_currently_open=True,
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete('/api/institutions/profile/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Institution.objects.filter(owner=user).exists())

    def test_institution_profile_does_not_allow_patch(self):
        user = User.objects.create_user(
            username='institution', password='StrongPass123', role=User.Role.INSTITUTION,
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch('/api/institutions/profile/', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

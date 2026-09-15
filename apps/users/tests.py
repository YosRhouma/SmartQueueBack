import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.users.models import CitizenProfile, User


class AuthAPITest(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        url = reverse('register')
        payload = {
            'username': 'demo_user',
            'email': 'demo@example.com',
            'password': 'StrongPass123',
            'role': User.Role.CITIZEN,
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='demo_user').exists())
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_accepts_email_and_password(self):
        user = User.objects.create_user(
            username='demo_user',
            email='demo@example.com',
            password='StrongPass123',
            first_name='Demo',
            last_name='User',
            phone='+21200000000',
            role=User.Role.CITIZEN,
        )

        url = reverse('login')
        response = self.client.post(url, {
            'email': 'demo@example.com',
            'password': 'StrongPass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_citizen_can_create_profile_after_registration(self):
        user = User.objects.create_user(
            username='citizen', password='StrongPass123', role=User.Role.CITIZEN,
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('citizen-profile'), {
            'firstName': 'Demo',
            'lastName': 'Citizen',
            'phone': '+21620000000',
            'email': 'citizen@example.com',
            'cin': '12345678',
            'dateOfBirth': '1995-01-15',
            'gender': 'female',
            'profilePicture': SimpleUploadedFile(
                'profile.png',
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0dIDATx\x9cc\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82',
                content_type='image/png',
            ),
            'Localisation': json.dumps({'governorate': 'Tunis', 'address': '1 Avenue Habib Bourguiba'}),
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['Localisation']['governorate'], 'Tunis')

    def test_citizen_can_delete_own_profile(self):
        user = User.objects.create_user(
            username='citizen', password='StrongPass123', role=User.Role.CITIZEN,
        )
        CitizenProfile.objects.create(
            user=user, first_name='Demo', last_name='Citizen', phone='+21620000000',
            email='citizen@example.com', cin='12345678', date_of_birth='1995-01-15', gender='female',
            governorate='Tunis', address='1 Avenue Habib Bourguiba',
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete(reverse('citizen-profile'))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CitizenProfile.objects.filter(user=user).exists())

    def test_citizen_profile_does_not_allow_patch(self):
        user = User.objects.create_user(
            username='citizen', password='StrongPass123', role=User.Role.CITIZEN,
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(reverse('citizen-profile'), {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

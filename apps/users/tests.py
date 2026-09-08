from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models import User


class AuthAPITest(APITestCase):
    def test_register_creates_user_and_returns_tokens(self):
        url = reverse('register')
        payload = {
            'username': 'demo_user',
            'email': 'demo@example.com',
            'password': 'StrongPass123',
            'password_confirm': 'StrongPass123',
            'first_name': 'Demo',
            'last_name': 'User',
            'phone': '+21200000000',
            'role': User.Role.CITIZEN,
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='demo_user').exists())
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_accepts_username_and_password(self):
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
            'username': 'demo_user',
            'password': 'StrongPass123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

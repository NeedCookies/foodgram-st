from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import User

# Create your tests here.

class PasswordValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')  # Обычно user-list для ModelViewSet
        self.password_url = reverse('user-set-password')  # Обычно user-set-password для @action
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='validPass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_short_password(self):
        data = {
            'username': 'shortuser',
            'email': 'short@example.com',
            'password': '1234567',
            'first_name': 'Short',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Пароль должен содержать не менее 8 символов.', str(response.data))

    def test_password_same_as_username(self):
        data = {
            'username': 'sameuser',
            'email': 'same@example.com',
            'password': 'sameuser',
            'first_name': 'Same',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Пароль не должен совпадать с именем пользователя.', str(response.data))

    def test_password_only_digits(self):
        data = {
            'username': 'digituser',
            'email': 'digit@example.com',
            'password': '12345678',
            'first_name': 'Digit',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('Пароль не может состоять только из цифр.', str(response.data))

    def test_valid_password(self):
        data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'validPass123',
            'first_name': 'Valid',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)

    def test_set_password_short(self):
        response = self.client.post(self.password_url, {
            'current_password': 'validPass123',
            'new_password': '1234567',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Пароль должен содержать не менее 8 символов.', str(response.data))

    def test_set_password_same_as_username(self):
        response = self.client.post(self.password_url, {
            'current_password': 'validPass123',
            'new_password': 'testuser',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Пароль не должен совпадать с именем пользователя.', str(response.data))

    def test_set_password_only_digits(self):
        response = self.client.post(self.password_url, {
            'current_password': 'validPass123',
            'new_password': '12345678',
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Пароль не может состоять только из цифр.', str(response.data))

    def test_set_password_valid(self):
        response = self.client.post(self.password_url, {
            'current_password': 'validPass123',
            'new_password': 'NewValidPass123',
        })
        self.assertEqual(response.status_code, 204)

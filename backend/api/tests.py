from django.contrib.auth import get_user_model
from django.test import TestCase


class AuthenticationApiTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='ada@example.com', password='secret-pass')

    def test_login_me_and_logout(self) -> None:
        login_response = self.client.post(
            '/api/login', data={'email': self.user.email, 'password': 'secret-pass'}, content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json()['email'], self.user.email)

        me_response = self.client.get('/api/auth/me')
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()['id'], self.user.id)

        logout_response = self.client.post('/api/logout')
        self.assertEqual(logout_response.status_code, 204)
        self.assertEqual(self.client.get('/api/auth/me').status_code, 401)

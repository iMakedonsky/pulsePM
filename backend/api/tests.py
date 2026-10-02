from django.contrib.auth import get_user_model
from django.test import TestCase


class AuthenticationApiTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='ada@example.com', password='78S28130s')

    def test_login_me_and_logout(self) -> None:
        login_response = self.client.post(
            '/api/auth/login', data={'email': self.user.email, 'password': '78S28130s'}, content_type='application/json'
        )
        self.assertEqual(200, login_response.status_code)
        self.assertEqual(login_response.json()['email'], self.user.email)
        self.assertEqual(200, self.client.get('/api/user/profile').status_code)

        logout_response = self.client.post('/api/auth/logout')
        self.assertEqual(204, logout_response.status_code)
        self.assertEqual(401, self.client.get('/api/user/profile').status_code)

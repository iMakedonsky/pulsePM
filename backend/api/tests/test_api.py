from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.test import TestCase

from organizations.models import Member, Organization

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse


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

    def test_register_invalid_email_is_400(self) -> None:
        response = self.client.post(
            '/api/auth/register',
            data={'email': 'not-an-email', 'password': '78S28130s'},
            content_type='application/json',
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual({'detail': 'Enter a valid email address.'}, response.json())


class OrganizationApiTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='ada@example.com', password='78S28130s')
        self.client.force_login(self.user)

    def create(self, name: str = 'Acme') -> _MonkeyPatchedWSGIResponse:
        return self.client.post(
            '/api/organization/create',
            data={'user_id': self.user.pk, 'name': name, 'description': 'desc'},
            content_type='application/json',
        )

    def test_create_second_owned_organization_is_409(self) -> None:
        self.assertEqual(200, self.create().status_code)
        response = self.create('Other')
        self.assertEqual(409, response.status_code)
        self.assertEqual(1, Organization.objects.filter(owner=self.user).count())

    def test_create_allowed_when_only_contributor_elsewhere(self) -> None:
        other = get_user_model().objects.create_user(email='bob@example.com', password='78S28130s')
        org = Organization.objects.create(owner=other, name='Bob inc', description='desc')
        Member.objects.create(user=self.user, organization=org)
        self.assertEqual(200, self.create().status_code)

    def test_non_numeric_id_is_400(self) -> None:
        for path in ('asda', 'asda/workspaces', 'asda/members'):
            with self.subTest(path=path):
                response = self.client.get(f'/api/organization/{path}')
                self.assertEqual(400, response.status_code)
                self.assertEqual({'detail': 'Invalid org_id.'}, response.json())

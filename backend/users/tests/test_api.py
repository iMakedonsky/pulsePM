import time
import uuid
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.core.signing import TimestampSigner, b64_encode
from django.test import Client

from api.openapi_docs import documented_messages, documented_statuses
from organizations.models import Member, Organization, OrgInvitation
from users.models import User

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse


@pytest.mark.django_db
def test_user_uses_email_as_login_identifier() -> None:
    user = get_user_model().objects.create_user(email='person@example.com', password='safe-password')

    assert user.username is None
    assert user.email == 'person@example.com'
    assert authenticate(username='person@example.com', password='safe-password') == user


@pytest.mark.django_db
def test_email_is_required() -> None:
    with pytest.raises(ValueError, match='email address'):
        get_user_model().objects.create_user(email='', password='safe-password')


# --- API error messages vs. the OpenAPI docs --------------------------------

PASSWORD = 'Str0ng-pass-phrase!'


@pytest.fixture
def user() -> User:
    return User.objects.create_user(email='ada@example.com', password=PASSWORD)


@pytest.fixture
def invitation() -> OrgInvitation:
    owner = User.objects.create_user(email='owner@example.com', password=PASSWORD)
    organization = Organization.objects.create(owner=owner, name='Acme', description='Test org')
    sender = Member.objects.create(user=owner, organization=organization, role=Member.OrgRoles.OWNER)
    return OrgInvitation.objects.create(email='invitee@example.com', sender=sender, org_invite=organization)


def post_register(client: Client, email: str, password: str, token: str | None = None) -> _MonkeyPatchedWSGIResponse:
    url = '/api/auth/register' + (f'?token={token}' if token else '')
    return client.post(url, {'email': email, 'password': password}, content_type='application/json')


def post_login(client: Client, email: str, password: str) -> _MonkeyPatchedWSGIResponse:
    return client.post('/api/auth/login', {'email': email, 'password': password}, content_type='application/json')


def assert_documented(response: _MonkeyPatchedWSGIResponse, status: int, path: str) -> None:
    assert response.status_code == status
    detail = response.json()['detail']
    assert detail in documented_messages('post', path, status), f'{status} {path}: {detail!r} is not in the API docs'


@pytest.mark.django_db
class TestRegisterErrorMessages:
    path = '/api/auth/register'

    def test_weak_password_is_400(self, client: Client) -> None:
        response = post_register(client, 'new@example.com', '123')
        assert_documented(response, 400, self.path)
        assert response.json() == {'detail': 'Provided password is invalid.'}

    def test_email_not_matching_invitation_is_400(self, client: Client, invitation: OrgInvitation) -> None:
        token = signing.dumps(invitation.id.int)
        response = post_register(client, 'someone-else@example.com', PASSWORD, token)
        assert_documented(response, 400, self.path)
        assert response.json() == {'detail': 'Registration email does not match the invitation.'}

    def test_malformed_invitation_id_is_400(self, client: Client) -> None:
        # Correctly signed, but the payload is not JSON, so `signing.loads` raises ValueError.
        token = TimestampSigner(salt='django.core.signing').sign(b64_encode(b'not json').decode())
        response = post_register(client, 'new@example.com', PASSWORD, token)
        assert_documented(response, 400, self.path)
        assert response.json() == {'detail': 'Invalid data'}

    def test_unknown_invitation_is_404(self, client: Client) -> None:
        response = post_register(client, 'new@example.com', PASSWORD, signing.dumps(uuid.uuid4().int))
        assert_documented(response, 404, self.path)
        assert response.json() == {'detail': 'Invitation with that ID does not exist.'}

    def test_existing_email_is_409(self, client: Client, user: User) -> None:
        response = post_register(client, user.email, PASSWORD)
        assert_documented(response, 409, self.path)
        assert response.json() == {'detail': 'User already exists with the same email.'}

    def test_tampered_token_is_410(self, client: Client) -> None:
        response = post_register(client, 'new@example.com', PASSWORD, 'not-a-signed-token')
        assert_documented(response, 410, self.path)
        assert response.json() == {'detail': 'Token invalid!'}

    def test_rejected_invitation_is_400(self, client: Client, invitation: OrgInvitation) -> None:
        invitation.accepted = False
        invitation.save()
        token = signing.dumps(invitation.id.int)
        response = post_register(client, invitation.email, PASSWORD, token)
        assert_documented(response, 400, self.path)
        assert response.json() == {'detail': 'Invitation was rejected.'}
        assert not User.objects.filter(email=invitation.email).exists()

    def test_token_older_than_max_age_is_410(self, client: Client, invitation: OrgInvitation) -> None:
        token = signing.dumps(invitation.id.int)
        with patch('django.core.signing.time.time', return_value=time.time() + 3600):
            response = post_register(client, invitation.email, PASSWORD, token)
        assert_documented(response, 410, self.path)
        assert response.json() == {'detail': 'Invitation token has expired!'}
        assert not User.objects.filter(email=invitation.email).exists()

    def test_every_documented_error_status_is_declared(self) -> None:
        assert documented_statuses('post', self.path) == {200, 400, 404, 409, 410}


@pytest.mark.django_db
class TestLoginErrorMessages:
    path = '/api/auth/login'

    def test_wrong_password_is_401(self, client: Client, user: User) -> None:
        response = post_login(client, user.email, 'wrong-password')
        assert_documented(response, 401, self.path)
        assert response.json() == {'detail': 'Invalid email or password.'}

    def test_unknown_email_is_401(self, client: Client) -> None:
        response = post_login(client, 'nobody@example.com', PASSWORD)
        assert_documented(response, 401, self.path)
        assert response.json() == {'detail': 'Invalid email or password.'}

    def test_unknown_email_and_wrong_password_are_indistinguishable(self, client: Client, user: User) -> None:
        wrong_password = post_login(client, user.email, 'wrong-password')
        unknown_email = post_login(client, 'nobody@example.com', PASSWORD)
        assert wrong_password.json() == unknown_email.json()

    def test_every_documented_error_status_is_declared(self) -> None:
        assert documented_statuses('post', self.path) == {200, 401}


@pytest.mark.django_db
class TestLogoutResponse:
    path = '/api/auth/logout'

    def test_logout_has_no_documented_errors_and_returns_204(self, client: Client, user: User) -> None:
        client.force_login(user)
        assert documented_statuses('post', self.path) == {204}

        response = client.post(self.path)
        assert response.status_code == 204
        assert response.content == b''
        assert '_auth_user_id' not in client.session

    def test_logout_without_session_still_204(self, client: Client) -> None:
        response = client.post(self.path)
        assert response.status_code == 204
        assert response.content == b''

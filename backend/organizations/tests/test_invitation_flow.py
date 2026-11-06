"""End-to-end invitation flow: a member invites via the API, Mailpit gets the mail, the invitee acts on the token.

The happy-path tests need a running Mailpit (`EMAIL_SERVICE_HOST:EMAIL_HTTP_PORT`) and are skipped without one.
The error tests only need the database.
"""

import re
import time
import uuid
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest
import requests
from django.core import signing
from django.core.signing import TimestampSigner, b64_encode
from django.test import Client

from api.openapi_docs import documented_messages, documented_statuses
from conf.settings import EMAIL_HTTP_PORT, EMAIL_SERVICE_HOST, FRONTED_ORIGIN
from organizations.models import Member, Organization, OrgInvitation
from users.models import User

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse as TestHttpResponse

OPEN_ENDPOINT = ('get', '/api/invitation/{invite_token}')
ANSWER_ENDPOINT = ('patch', '/api/invitation/{invite_token}/accept')
LIST_ENDPOINT = ('get', '/api/organization/{org_id}/invitations')
MAILPIT_API = f'http://{EMAIL_SERVICE_HOST}:{EMAIL_HTTP_PORT}/api/v1'
TOKEN_IN_MAIL = re.compile(rf'{re.escape(FRONTED_ORIGIN)}/invitation/(\S+)')
PASSWORD = 'Str0ng-pass-phrase!'
NO_LONGER_VALID = 'The invitation is no longer valid.'
REJECTED = NO_LONGER_VALID


# --- fixtures and helpers ----------------------------------------------------


@pytest.fixture
def mailpit() -> None:
    try:
        requests.get(f'{MAILPIT_API}/info', timeout=2).raise_for_status()
    except requests.RequestException:
        pytest.skip(f'Mailpit is not reachable at {MAILPIT_API}')


@pytest.fixture
def invitee_email(mailpit: None) -> Iterator[str]:  # noqa: ARG001
    """A fresh address nobody has registered; its Mailpit messages are removed afterwards."""
    email = f'invitee-{uuid.uuid4().hex[:10]}@example.com'
    yield email
    requests.delete(f'{MAILPIT_API}/search', params={'query': f'to:{email}'}, timeout=5)


@pytest.fixture
def owner() -> User:
    return User.objects.create_user(email='owner@example.com', password=PASSWORD)


@pytest.fixture
def organization(owner: User) -> Organization:
    return Organization.objects.create(owner=owner, name='Acme', description='Test org')


@pytest.fixture
def sender(owner: User, organization: Organization) -> Member:
    return Member.objects.create(user=owner, organization=organization, role=Member.OrgRoles.OWNER)


def send_invitation(email: str, sender: Member) -> str:
    """Create the invitation as the organization's member (API -> Mailpit) and return the token from the mail."""
    sender_client = Client()
    sender_client.force_login(sender.user)
    response = sender_client.post(
        f'/api/organization/{sender.organization_id}/invitation/create',
        {'email': email, 'text_message': 'Join us'},
        content_type='application/json',
    )
    assert response.status_code == 201, f'invitation was not created: {response.content!r}'
    assert OrgInvitation.objects.filter(email=email).exists()

    found = requests.get(f'{MAILPIT_API}/search', params={'query': f'to:{email}'}, timeout=5).json()
    if found['messages']:
        message = requests.get(f'{MAILPIT_API}/message/{found["messages"][0]["ID"]}', timeout=5).json()
        match = TOKEN_IN_MAIL.search(message['Text'])
        assert match, f'no invitation link in the mail body: {message["Text"]!r}'
        return match.group(1)
    pytest.fail(f'no mail for {email} reached Mailpit')


def invitation_url(token: str, *, accept: bool = False) -> str:
    return f'/api/invitation/{token}' + ('/accept' if accept else '')


def get_invitation(client: Client, token: str) -> TestHttpResponse:
    return client.get(invitation_url(token))


def answer(client: Client, token: str, payload: Any) -> TestHttpResponse:
    return client.patch(invitation_url(token, accept=True), payload, content_type='application/json')


def register(client: Client, email: str, token: str | None = None) -> TestHttpResponse:
    url = '/api/auth/register' + (f'?token={token}' if token else '')
    return client.post(url, {'email': email, 'password': PASSWORD}, content_type='application/json')


def login(client: Client, email: str) -> TestHttpResponse:
    return client.post('/api/auth/login', {'email': email, 'password': PASSWORD}, content_type='application/json')


# --- happy paths -------------------------------------------------------------


@pytest.mark.django_db
class TestInvitationFlow:
    def test_new_user_registers_with_token_and_joins_organization(
        self, invitee_email: str, organization: Organization, sender: Member
    ) -> None:
        token = send_invitation(invitee_email, sender)

        invitation = OrgInvitation.objects.get(email=invitee_email)
        assert signing.loads(token) == invitation.id.int
        assert invitation.accepted is None
        assert not User.objects.filter(email=invitee_email).exists()

        client = Client()
        opened = get_invitation(client, token)
        assert opened.status_code == 200
        body = opened.json()
        assert body['org_invite'] == organization.pk
        assert body['accepted'] is None

        # The frontend pre-fills the sign-up form with the invited address.
        registered = register(client, body['email'], token)
        assert registered.status_code == 200
        assert registered.json()['email'] == invitee_email

        user = User.objects.get(email=invitee_email)
        invitation = OrgInvitation.objects.get(pk=invitation.pk)
        assert invitation.accepted is True
        member = Member.objects.get(user=user, organization=organization)
        assert member.role == Member.OrgRoles.CONTRIBUTOR

        logged_in = login(client, invitee_email)
        assert logged_in.status_code == 200
        memberships = client.get('/api/user/memberships/')
        assert memberships.status_code == 200
        assert [item['organization']['id'] for item in memberships.json()] == [organization.pk]

    def test_new_user_refuses_invitation(self, invitee_email: str, organization: Organization, sender: Member) -> None:
        token = send_invitation(invitee_email, sender)
        client = Client()
        assert get_invitation(client, token).status_code == 200

        refused = answer(client, token, {'accepted': False})
        assert refused.status_code == 200
        assert refused.json() == {'accepted': False, 'member': None}

        invitation = OrgInvitation.objects.get(email=invitee_email)
        assert invitation.accepted is False
        assert not Member.objects.filter(organization=organization).exclude(pk=sender.pk).exists()
        assert not User.objects.filter(email=invitee_email).exists()

        # A refused invitation is closed: it can no longer be opened, accepted or used to sign up.
        assert_error(get_invitation(client, token), 410, REJECTED)
        assert_error(answer(client, token, {'accepted': True}), 410, REJECTED)
        assert_error(register(client, invitee_email, token), 410, REJECTED)
        assert not User.objects.filter(email=invitee_email).exists()
        assert not Member.objects.filter(organization=organization).exclude(pk=sender.pk).exists()

    def test_existing_user_accepts_invitation(
        self, invitee_email: str, organization: Organization, sender: Member
    ) -> None:
        user = User.objects.create_user(email=invitee_email, password=PASSWORD)
        token = send_invitation(invitee_email, sender)
        client = Client()

        accepted = answer(client, token, {'accepted': True})

        assert accepted.status_code == 200
        assert accepted.json()['accepted'] is True
        assert accepted.json()['member']['organization'] == organization.pk
        assert Member.objects.get(user=user, organization=organization).role == Member.OrgRoles.CONTRIBUTOR
        assert OrgInvitation.objects.get(email=invitee_email).accepted is True


# --- error paths -------------------------------------------------------------


@pytest.fixture
def invitation(organization: Organization, sender: Member) -> OrgInvitation:
    return OrgInvitation.objects.create(email='invitee@example.com', sender=sender, org_invite=organization)


@pytest.fixture
def token(invitation: OrgInvitation) -> str:
    return signing.dumps(invitation.id.int)


def assert_error(response: TestHttpResponse, status: int, detail: str, endpoint: tuple[str, str] | None = None) -> None:
    """Check status and exact message; with `endpoint`, also that the message is listed in the API docs."""
    assert (response.status_code, response.json()) == (status, {'detail': detail})
    if endpoint is not None:
        method, path = endpoint
        assert detail in documented_messages(method, path, status), f'{status} {detail!r} is not in the API docs'


def validly_signed_garbage() -> str:
    """Carries a correct signature but a payload that is not JSON."""
    return TimestampSigner(salt='django.core.signing').sign(b64_encode(b'not json').decode())


@pytest.mark.django_db
class TestOpenInvitationErrors:
    @pytest.mark.parametrize('bad_token', ['not-a-signed-token', 'a:b:c', '.', 'x' * 300])
    def test_tampered_token_is_410(self, client: Client, bad_token: str) -> None:
        assert_error(get_invitation(client, bad_token), 410, 'Token invalid!', OPEN_ENDPOINT)

    def test_token_signed_with_foreign_key_is_410(self, client: Client, invitation: OrgInvitation) -> None:
        foreign = signing.dumps(invitation.id.int, key='some-other-secret-key')
        assert_error(get_invitation(client, foreign), 410, 'Token invalid!', OPEN_ENDPOINT)

    def test_token_with_non_json_payload_is_410(self, client: Client) -> None:
        assert_error(get_invitation(client, validly_signed_garbage()), 400, 'Invalid data', OPEN_ENDPOINT)

    def test_unknown_invitation_is_404(self, client: Client) -> None:
        assert_error(
            get_invitation(client, signing.dumps(uuid.uuid4().int)), 404, 'Invitation with that ID does not exist.'
        )

    def test_token_older_than_thirty_minutes_is_410(self, client: Client, token: str) -> None:
        with patch('django.core.signing.time.time', return_value=time.time() + 31 * 60):
            response = get_invitation(client, token)
        assert_error(response, 410, 'Invitation token has expired!', OPEN_ENDPOINT)

    def test_token_just_under_thirty_minutes_is_still_valid(self, client: Client, token: str) -> None:
        with patch('django.core.signing.time.time', return_value=time.time() + 29 * 60):
            response = get_invitation(client, token)
        assert response.status_code == 200


@pytest.fixture
def rejected_invitation(invitation: OrgInvitation) -> OrgInvitation:
    invitation.accepted = False
    invitation.save()
    return invitation


@pytest.mark.django_db
@pytest.mark.usefixtures('rejected_invitation')
class TestRejectedInvitation:
    """An invitation already marked `accepted=False` is closed on every endpoint, even with a fresh token."""

    def test_opening_is_410(self, client: Client, token: str) -> None:
        assert_error(get_invitation(client, token), 410, REJECTED, OPEN_ENDPOINT)

    @pytest.mark.parametrize('accepted', [True, False])
    def test_answering_is_410_and_adds_no_member(
        self, client: Client, invitation: OrgInvitation, token: str, *, accepted: bool
    ) -> None:
        User.objects.create_user(email=invitation.email, password=PASSWORD)
        assert_error(answer(client, token, {'accepted': accepted}), 410, REJECTED, ANSWER_ENDPOINT)
        assert not Member.objects.filter(user__email=invitation.email).exists()
        invitation.refresh_from_db()
        assert invitation.accepted is False

    def test_signing_up_is_410_and_creates_no_user(self, client: Client, invitation: OrgInvitation, token: str) -> None:
        assert_error(register(client, invitation.email, token), 410, REJECTED)
        assert not User.objects.filter(email=invitation.email).exists()

    def test_message_is_documented(self) -> None:
        assert REJECTED in documented_messages(*OPEN_ENDPOINT, 410)
        assert REJECTED in documented_messages(*ANSWER_ENDPOINT, 410)


@pytest.mark.django_db
class TestAnswerInvitationErrors:
    def test_tampered_token_is_410(self, client: Client) -> None:
        assert_error(answer(client, 'not-a-signed-token', {'accepted': True}), 410, 'Token invalid!', ANSWER_ENDPOINT)

    def test_token_with_non_json_payload_is_410(self, client: Client) -> None:
        assert_error(answer(client, validly_signed_garbage(), {'accepted': True}), 400, 'Invalid data', ANSWER_ENDPOINT)

    def test_unknown_invitation_is_404(self, client: Client) -> None:
        response = answer(client, signing.dumps(uuid.uuid4().int), {'accepted': True})
        assert_error(response, 404, 'Invitation with that ID does not exist.', ANSWER_ENDPOINT)

    def test_token_older_than_thirty_minutes_is_410_and_adds_no_member(
        self, client: Client, invitation: OrgInvitation, token: str
    ) -> None:
        User.objects.create_user(email=invitation.email, password=PASSWORD)
        with patch('django.core.signing.time.time', return_value=time.time() + 31 * 60):
            response = answer(client, token, {'accepted': True})
        assert_error(response, 410, 'Invitation token has expired!', ANSWER_ENDPOINT)
        assert not Member.objects.filter(user__email=invitation.email).exists()
        invitation.refresh_from_db()
        assert invitation.accepted is None

    def test_accepting_before_signing_up_is_404(self, client: Client, invitation: OrgInvitation, token: str) -> None:
        # The text embeds the invitee's address, so it is checked exactly; the docs hold a sample address.
        assert_error(
            answer(client, token, {'accepted': True}),
            404,
            f'User with email "{invitation.email}" does not exist. '
            'First create own account then login in and try to accept again!',
        )
        invitation.refresh_from_db()
        assert invitation.accepted is None

    def test_accepting_twice_is_410_and_adds_no_second_member(
        self, client: Client, invitation: OrgInvitation, token: str, organization: Organization
    ) -> None:
        user = User.objects.create_user(email=invitation.email, password=PASSWORD)
        assert answer(client, token, {'accepted': True}).status_code == 200
        assert_error(answer(client, token, {'accepted': True}), 410, NO_LONGER_VALID, ANSWER_ENDPOINT)
        assert Member.objects.filter(user=user, organization=organization).count() == 1

    def test_already_a_member_is_409_and_leaves_invitation_open(
        self, client: Client, invitation: OrgInvitation, token: str, organization: Organization
    ) -> None:
        user = User.objects.create_user(email=invitation.email, password=PASSWORD)
        Member.objects.create(user=user, organization=organization)
        assert_error(
            answer(client, token, {'accepted': True}),
            409,
            f'The user {user} is already invited to organization {organization}.',
        )
        invitation.refresh_from_db()
        assert invitation.accepted is None

    @pytest.mark.parametrize(
        ('payload', 'detail'),
        [
            ({}, 'Invalid accepted: Field required'),
            ({'accepted': 'maybe'}, 'Invalid accepted: Input should be a valid boolean, unable to interpret input'),
        ],
    )
    def test_invalid_payload_is_410(self, client: Client, token: str, payload: dict[str, Any], detail: str) -> None:
        assert_error(answer(client, token, payload), 400, detail)

    def test_unparsable_body_is_410(self, client: Client, token: str) -> None:
        assert_error(answer(client, token, 'not json'), 400, 'Cannot parse request body')


@pytest.mark.django_db
class TestSignUpWithInvitationErrors:
    def test_signing_up_with_another_email_is_410_and_creates_no_user(
        self, client: Client, invitation: OrgInvitation, token: str
    ) -> None:
        assert_error(
            register(client, 'someone-else@example.com', token),
            400,
            'Registration email does not match the invitation.',
        )
        assert not User.objects.filter(email='someone-else@example.com').exists()
        invitation.refresh_from_db()
        assert invitation.accepted is None

    def test_signing_up_with_tampered_token_is_410_and_creates_no_user(
        self, client: Client, invitation: OrgInvitation
    ) -> None:
        assert_error(register(client, invitation.email, 'not-a-signed-token'), 410, 'Token invalid!')
        assert not User.objects.filter(email=invitation.email).exists()

    def test_signing_up_with_token_older_than_thirty_minutes_rolls_back_the_user(
        self, client: Client, invitation: OrgInvitation, token: str
    ) -> None:
        with patch('django.core.signing.time.time', return_value=time.time() + 31 * 60):
            response = register(client, invitation.email, token)
        assert_error(response, 410, 'Invitation token has expired!')
        assert not User.objects.filter(email=invitation.email).exists()
        invitation.refresh_from_db()
        assert invitation.accepted is None

    def test_signing_up_with_unknown_invitation_is_404_and_creates_no_user(
        self, client: Client, invitation: OrgInvitation
    ) -> None:
        response = register(client, invitation.email, signing.dumps(uuid.uuid4().int))
        assert_error(response, 404, 'Invitation with that ID does not exist.')
        assert not User.objects.filter(email=invitation.email).exists()


# --- GET /api/organization/{org_id}/invitations -------------------------------


@pytest.mark.django_db
class TestListInvitations:
    @staticmethod
    def url(org_id: object) -> str:
        return f'/api/organization/{org_id}/invitations'

    @pytest.fixture
    def signed_in(self, client: Client, owner: User, sender: Member) -> Client:  # noqa: ARG002
        client.force_login(owner)
        return client

    def test_declared_statuses(self) -> None:
        assert documented_statuses(*LIST_ENDPOINT) == {200, 400, 403, 404}

    def test_200_returns_invitations_with_sender_name(
        self, signed_in: Client, organization: Organization, invitation: OrgInvitation, owner: User
    ) -> None:
        response = signed_in.get(self.url(organization.pk))

        assert response.status_code == 200
        [item] = response.json()
        assert item['id'] == str(invitation.id)
        assert item['sender_name'] == owner.email
        assert isinstance(item['sender_name'], str)
        assert item['org_invite'] == organization.pk
        assert item['email'] == invitation.email
        assert item['accepted'] is None
        assert {'created_at', 'expired_at'} <= item.keys()
        assert 'org_name' not in item

    def test_200_lists_newest_first(
        self, signed_in: Client, organization: Organization, sender: Member, invitation: OrgInvitation
    ) -> None:
        newer = OrgInvitation.objects.create(email='newer@example.com', sender=sender, org_invite=organization)

        response = signed_in.get(self.url(organization.pk))

        assert [item['id'] for item in response.json()] == [str(newer.id), str(invitation.id)]

    def test_200_sender_name_is_each_invitations_own_sender(
        self, signed_in: Client, organization: Organization, sender: Member, invitation: OrgInvitation
    ) -> None:
        colleague = Member.objects.create(
            user=User.objects.create_user(email='pm@example.com', password=PASSWORD),
            organization=organization,
            role=Member.OrgRoles.PM,
        )
        OrgInvitation.objects.create(email='other@example.com', sender=colleague, org_invite=organization)

        senders = {item['email']: item['sender_name'] for item in signed_in.get(self.url(organization.pk)).json()}

        assert senders == {invitation.email: sender.user.email, 'other@example.com': 'pm@example.com'}

    @pytest.mark.usefixtures('invitation')
    def test_200_shows_current_status_after_the_invitee_answers(
        self, signed_in: Client, organization: Organization, token: str
    ) -> None:
        assert answer(Client(), token, {'accepted': False}).status_code == 200

        [item] = signed_in.get(self.url(organization.pk)).json()

        assert item['accepted'] is False

    def test_200_leaves_out_other_organizations(
        self, signed_in: Client, organization: Organization, invitation: OrgInvitation
    ) -> None:
        stranger = User.objects.create_user(email='stranger@example.com', password=PASSWORD)
        other = Organization.objects.create(owner=stranger, name='Other', description='Other org')
        other_member = Member.objects.create(user=stranger, organization=other, role=Member.OrgRoles.OWNER)
        OrgInvitation.objects.create(email='foreign@example.com', sender=other_member, org_invite=other)

        response = signed_in.get(self.url(organization.pk))

        assert [item['id'] for item in response.json()] == [str(invitation.id)]

    def test_400_non_numeric_org_id(self, signed_in: Client) -> None:
        assert_error(signed_in.get(self.url('abc')), 400, 'Invalid org_id.', LIST_ENDPOINT)

    @pytest.mark.usefixtures('invitation')
    def test_403_not_a_member(self, client: Client, organization: Organization) -> None:
        outsider = User.objects.create_user(email='outsider@example.com', password=PASSWORD)
        client.force_login(outsider)
        assert_error(
            client.get(self.url(organization.pk)),
            403,
            'Current User is not a member of the Organization.',
            LIST_ENDPOINT,
        )

    @pytest.mark.usefixtures('sender')
    def test_403_anonymous(self, client: Client, organization: Organization) -> None:
        assert_error(
            client.get(self.url(organization.pk)),
            403,
            'Current User is not a member of the Organization.',
            LIST_ENDPOINT,
        )

    def test_404_organization_without_invitations(self, signed_in: Client, organization: Organization) -> None:
        assert_error(
            signed_in.get(self.url(organization.pk)),
            404,
            'This organization has no invitations yet.',
            LIST_ENDPOINT,
        )

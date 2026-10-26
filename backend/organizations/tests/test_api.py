import time
import uuid
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from django.core import signing
from django.test import Client, TestCase

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse

from api.openapi_docs import documented_messages, documented_statuses
from organizations.models import Member, Organization, OrgInvitation, WorkSpace
from users.models import User


class PulseTest(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(email='1ttest@example.com', password='')

    def test_user_create(self) -> None:
        user = User.objects.filter(email='1ttest@example.com').values_list('email', flat=True)
        self.assertEqual(user[0], '1ttest@example.com')


class InvitationApiTest(TestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create_user(email='owner@example.com', password='')
        self.invitee = User.objects.create_user(email='invitee@example.com', password='')
        self.organization = Organization.objects.create(owner=self.owner, name='Acme', description='Test org')
        self.sender = Member.objects.create(user=self.owner, organization=self.organization, role=Member.OrgRoles.OWNER)
        self.invitation = OrgInvitation.objects.create(
            email='Invitee@example.com', sender=self.sender, org_invite=self.organization
        )
        self.token = signing.dumps(self.invitation.id.int)

    def url(self, invite_token: object, *, accept: bool = False) -> str:
        return f'/api/invitation/{invite_token}' + ('/accept' if accept else '')

    def accept(self, token: object, *, accepted: bool = True) -> _MonkeyPatchedWSGIResponse:
        return self.client.patch(self.url(token, accept=True), {'accepted': accepted}, content_type='application/json')

    def test_get_returns_invitation_and_token(self) -> None:
        response = self.client.get(self.url(self.token))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['org_invite'], self.organization.id)
        self.assertEqual(body['email'], 'Invitee@example.com')
        self.assertEqual(body['text_message'], 'Invitation :)')
        self.assertIsNone(body['accepted'])

    def test_get_tampered_token_is_410(self) -> None:
        response = self.client.get(self.url('not-a-signed-token'))
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {'detail': 'Token invalid!'})

    def test_get_unknown_invitation_is_404(self) -> None:
        response = self.client.get(self.url(signing.dumps(uuid.uuid4().int)))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Invitation with that ID does not exist.'})

    def test_get_after_token_max_age_is_410(self) -> None:
        with patch('django.core.signing.time.time', return_value=time.time() + 3600):
            response = self.client.get(self.url(self.token))
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {'detail': 'Invitation token has expired!'})

    def test_patch_accept_creates_member(self) -> None:
        response = self.accept(self.token)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['accepted'])
        self.assertEqual(body['member']['user']['email'], 'invitee@example.com')
        self.assertEqual(body['member']['organization'], self.organization.id)
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.accepted)

    def test_patch_accept_twice_is_409(self) -> None:
        first = self.accept(self.token)
        second = self.accept(self.token)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(Member.objects.filter(user=self.invitee).count(), 1)
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.accepted)

    def test_patch_accept_when_already_member_is_409_and_leaves_state(self) -> None:
        Member.objects.create(user=self.invitee, organization=self.organization)
        response = self.accept(self.token)
        self.assertEqual(response.status_code, 409)
        self.invitation.refresh_from_db()
        self.assertIsNone(self.invitation.accepted)

    def test_patch_accept_unregistered_email_is_404_and_leaves_state(self) -> None:
        self.invitee.delete()
        response = self.accept(self.token)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'User with that email does not exist.'})
        self.invitation.refresh_from_db()
        self.assertIsNone(self.invitation.accepted)

    def test_patch_accept_after_token_max_age_is_410(self) -> None:
        with patch('django.core.signing.time.time', return_value=time.time() + 3600):
            response = self.accept(self.token)
        self.assertEqual(response.status_code, 410)
        self.assertFalse(Member.objects.filter(user=self.invitee).exists())

    def test_get_rejected_invitation_is_410(self) -> None:
        self.invitation.accepted = False
        self.invitation.save()
        response = self.client.get(self.url(self.token))
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {'detail': 'The invitation is no longer valid.'})

    def test_patch_accept_rejected_invitation_is_410(self) -> None:
        self.accept(self.token, accepted=False)
        response = self.accept(self.token)
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {'detail': 'The invitation is no longer valid.'})
        self.assertFalse(Member.objects.filter(user=self.invitee).exists())

    def test_patch_decline_sets_false_without_member(self) -> None:
        response = self.accept(self.token, accepted=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'accepted': False, 'member': None})
        self.invitation.refresh_from_db()
        self.assertFalse(self.invitation.accepted)
        self.assertFalse(Member.objects.filter(user=self.invitee).exists())


# --- API error messages vs. the OpenAPI docs --------------------------------

PASSWORD = 'Str0ng-pass-phrase!'


@pytest.fixture
def owner() -> User:
    return User.objects.create_user(email='owner@example.com', password=PASSWORD)


@pytest.fixture
def organization(owner: User) -> Organization:
    organization = Organization.objects.create(owner=owner, name='Acme', description='Test org')
    Member.objects.create(user=owner, organization=organization, role=Member.OrgRoles.OWNER)
    return organization


@pytest.fixture
def outsider() -> User:
    return User.objects.create_user(email='outsider@example.com', password=PASSWORD)


def assert_documented(
    response: _MonkeyPatchedWSGIResponse, method: str, path: str, status: int, message: str | None = None
) -> None:
    """Check the response has `status`, that its message is in the API docs and, if given, equals `message`."""
    assert response.status_code == status
    detail = response.json()['detail']
    assert detail in documented_messages(method, path, status), f'{status} {path}: {detail!r} is not in the API docs'
    if message is not None:
        assert detail == message


@pytest.mark.django_db
class TestCreateOrganizationErrorMessages:
    path = '/api/organization/create'

    def post(self, client: Client, **payload: str) -> _MonkeyPatchedWSGIResponse:
        return client.post(self.path, payload, content_type='application/json')

    def test_blank_name_is_410(self, client: Client, outsider: User) -> None:
        client.force_login(outsider)
        response = self.post(client, name='', description='Test org')
        assert_documented(response, 'post', self.path, 400, 'This field cannot be blank.')

    def test_too_long_name_is_410(self, client: Client, outsider: User) -> None:
        client.force_login(outsider)
        response = self.post(client, name='x' * 101, description='Test org')
        assert_documented(
            response, 'post', self.path, 400, 'Ensure this value has at most 100 characters (it has 101).'
        )

    @pytest.mark.usefixtures('organization')
    def test_second_organization_is_409(self, client: Client, owner: User) -> None:
        client.force_login(owner)
        response = self.post(client, name='Another', description='Test org')
        assert_documented(response, 'post', self.path, 409, 'User already owns an organization.')

    def test_declared_statuses(self) -> None:
        assert documented_statuses('post', self.path) == {200, 400, 409}


@pytest.mark.django_db
class TestGetOrganizationErrorMessages:
    path = '/api/organization/{org_id}'

    def get(self, client: Client, org_id: object) -> _MonkeyPatchedWSGIResponse:
        return client.get(f'/api/organization/{org_id}')

    def test_non_numeric_id_is_410(self, client: Client, owner: User) -> None:
        client.force_login(owner)
        assert_documented(self.get(client, 'abc'), 'get', self.path, 400, 'Invalid org_id.')

    def test_non_member_is_403(self, client: Client, outsider: User, organization: Organization) -> None:
        client.force_login(outsider)
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 403, 'Current User is not a member of the Organization.')

    def test_anonymous_is_403(self, client: Client, organization: Organization) -> None:
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 403, 'Current User is not a member of the Organization.')

    def test_unknown_organization_is_403_because_membership_is_checked_first(
        self, client: Client, owner: User, organization: Organization
    ) -> None:
        client.force_login(owner)
        response = self.get(client, organization.pk + 1000)
        assert_documented(response, 'get', self.path, 403, 'Current User is not a member of the Organization.')

    def test_declared_statuses(self) -> None:
        assert documented_statuses('get', self.path) == {200, 400, 403, 404}


@pytest.mark.django_db
class TestListWorkspacesErrorMessages:
    path = '/api/organization/{org_id}/workspaces'

    def get(self, client: Client, org_id: object) -> _MonkeyPatchedWSGIResponse:
        return client.get(f'/api/organization/{org_id}/workspaces')

    def test_non_numeric_id_is_410(self, client: Client, owner: User) -> None:
        client.force_login(owner)
        assert_documented(self.get(client, 'abc'), 'get', self.path, 400, 'Invalid org_id.')

    def test_non_member_is_403(self, client: Client, outsider: User, organization: Organization) -> None:
        client.force_login(outsider)
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 403, 'Current User is not a member of the Organization.')

    def test_organization_without_workspaces_is_404(
        self, client: Client, owner: User, organization: Organization
    ) -> None:
        client.force_login(owner)
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 404, 'This organization has no workspaces yet.')

    def test_workspace_of_another_organization_does_not_count(
        self, client: Client, owner: User, organization: Organization, outsider: User
    ) -> None:
        other = Organization.objects.create(owner=outsider, name='Other', description='Other org')
        other_member = Member.objects.create(user=outsider, organization=other, role=Member.OrgRoles.OWNER)
        WorkSpace.objects.create(
            created_by=other_member,
            organization=other,
            name='WS',
            space_code='WS1',
            icon_url='x',
            description='Other workspace',
        )
        client.force_login(owner)
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 404, 'This organization has no workspaces yet.')

    def test_declared_statuses(self) -> None:
        assert documented_statuses('get', self.path) == {200, 400, 403, 404}


@pytest.mark.django_db
class TestListMembersErrorMessages:
    path = '/api/organization/{org_id}/members'

    def get(self, client: Client, org_id: object) -> _MonkeyPatchedWSGIResponse:
        return client.get(f'/api/organization/{org_id}/members')

    def test_non_numeric_id_is_410(self, client: Client, owner: User) -> None:
        client.force_login(owner)
        assert_documented(self.get(client, 'abc'), 'get', self.path, 400, 'Invalid org_id.')

    def test_non_member_is_403(self, client: Client, outsider: User, organization: Organization) -> None:
        client.force_login(outsider)
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 403, 'Current User is not a member of the Organization.')

    def test_anonymous_is_403(self, client: Client, organization: Organization) -> None:
        response = self.get(client, organization.pk)
        assert_documented(response, 'get', self.path, 403, 'Current User is not a member of the Organization.')

    def test_declared_statuses(self) -> None:
        assert documented_statuses('get', self.path) == {200, 400, 403, 404}

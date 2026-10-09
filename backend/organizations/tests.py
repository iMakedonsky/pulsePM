import time
import uuid
from datetime import timedelta
from typing import TYPE_CHECKING
from unittest.mock import patch

from django.core import signing
from django.test import TestCase
from django.utils import timezone

if TYPE_CHECKING:
    from django.test.client import _MonkeyPatchedWSGIResponse

from organizations.models import Member, Organization, OrgInvitation
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
        self.assertEqual(body['invitation_token'], self.token)
        self.assertEqual(body['invitation']['org_invite'], self.organization.id)
        self.assertEqual(body['invitation']['email'], 'Invitee@example.com')
        self.assertEqual(body['invitation']['text_message'], 'Invitation :)')
        self.assertIsNone(body['invitation']['accepted'])

    def test_get_tampered_token_is_410(self) -> None:
        response = self.client.get(self.url('not-a-signed-token'))
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {'detail': 'Token expired!'})

    def test_get_unknown_invitation_is_404(self) -> None:
        response = self.client.get(self.url(signing.dumps(uuid.uuid4().int)))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'Invitation with that ID does not exist.'})

    def test_get_expired_invitation_is_410(self) -> None:
        self.invitation.expired_at = timezone.now() - timedelta(minutes=1)
        self.invitation.save()
        response = self.client.get(self.url(self.token))
        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.json(), {'detail': 'Invitation expired!'})

    def test_get_declined_invitation_is_410(self) -> None:
        self.invitation.accepted = False
        self.invitation.save()
        response = self.client.get(self.url(self.token))
        self.assertEqual(response.status_code, 410)

    def test_patch_accept_creates_member(self) -> None:
        response = self.accept(self.token)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['accepted'])
        self.assertEqual(body['member']['user']['email'], 'invitee@example.com')
        self.assertEqual(body['member']['organization'], self.organization.id)
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.accepted)

    def test_patch_accept_twice_returns_same_member(self) -> None:
        first = self.accept(self.token)
        second = self.accept(self.token)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.json()['member']['id'], second.json()['member']['id'])
        self.assertEqual(Member.objects.filter(user=self.invitee).count(), 1)

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

    def test_patch_accept_declined_invitation_is_410(self) -> None:
        self.accept(self.token, accepted=False)
        response = self.accept(self.token)
        self.assertEqual(response.status_code, 410)
        self.assertFalse(Member.objects.filter(user=self.invitee).exists())

    def test_patch_decline_sets_false_without_member(self) -> None:
        response = self.accept(self.token, accepted=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'accepted': False, 'member': None})
        self.invitation.refresh_from_db()
        self.assertFalse(self.invitation.accepted)
        self.assertFalse(Member.objects.filter(user=self.invitee).exists())

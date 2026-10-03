import uuid

from django.test import TestCase

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

    def url(self, invitation_id: object) -> str:
        return f'/api/invitation/{invitation_id}'

    def test_get_returns_organization_name(self) -> None:
        response = self.client.get(self.url(self.invitation.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'org_invite': 1, 'text_message': 'Invitation :)'})

    def test_get_malformed_uuid_is_400(self) -> None:
        response = self.client.get(self.url('not-a-uuid'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'detail': 'Invalid data'})

    def test_get_unknown_uuid_is_404(self) -> None:
        response = self.client.get(self.url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': "Invitation doesn't exist or invalid UUID"})

    def test_patch_accept_creates_contributor_member(self) -> None:
        response = self.client.patch(self.url(self.invitation.id), {'accepted': True}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['accepted'])
        self.assertEqual(body['member']['role'], Member.OrgRoles.CONTRIBUTOR)
        self.assertEqual(body['member']['user']['email'], 'invitee@example.com')
        self.invitation.refresh_from_db()
        self.assertTrue(self.invitation.accepted)

    def test_patch_accept_twice_returns_same_member(self) -> None:
        first = self.client.patch(self.url(self.invitation.id), {'accepted': True}, content_type='application/json')
        second = self.client.patch(self.url(self.invitation.id), {'accepted': True}, content_type='application/json')
        self.assertEqual(first.json()['member']['id'], second.json()['member']['id'])
        self.assertEqual(Member.objects.filter(user=self.invitee).count(), 1)

    def test_patch_accept_unregistered_email_is_404_and_leaves_state(self) -> None:
        self.invitee.delete()
        response = self.client.patch(self.url(self.invitation.id), {'accepted': True}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.invitation.refresh_from_db()
        self.assertIsNone(self.invitation.accepted)

    def test_patch_decline_sets_false_without_member(self) -> None:
        response = self.client.patch(self.url(self.invitation.id), {'accepted': False}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'accepted': False, 'member': None})
        self.assertFalse(Member.objects.filter(user=self.invitee).exists())

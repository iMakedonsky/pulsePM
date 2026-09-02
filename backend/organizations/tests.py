from django.test import TestCase

from users.models import User


class PulseTest(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(email='1ttest@example.com', password='')

    def test_user_create(self) -> None:
        user = User.objects.filter(email='1ttest@example.com').values_list('email', flat=True)
        self.assertEqual(user[0], '1ttest@example.com')

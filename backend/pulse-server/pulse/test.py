from django.test import TestCase
from users.models import User


class PulseTest(TestCase):
    def setUp(self):
        User.objects.create_user(username='1ttest', password='')

    def test_user_create(self):
        # self.assertEqual(create_user.save(), ValidationError)
        # self.assertEqual(create_user.save(), ValueError)
        user = User.objects.filter(username='1ttest').values_list('username', flat=True)
        self.assertEqual(user[0], '1ttest')

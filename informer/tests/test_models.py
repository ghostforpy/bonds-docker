from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import UserInformer

User = get_user_model()


class CreateUserInformerTest(TestCase):
    """class for user_informer tests"""

    def test_refresh_changes_function(self):

        user = User.objects.create(username="user1", password="password1")
        user_informer = UserInformer.objects.filter(user=user)
        self.assertEqual(1, user_informer.count())

#import json
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from ..utils import parse_request


User = get_user_model()


class TelegramChatAuthBackend(BaseBackend):
    def authenticate(self, tg_body):
        try:
            tg_user_id = tg_body.user_from.id
            try:
                user = User.objects.get(
                    socialaccount__uid=tg_user_id,
                    socialaccount__provider='telegram'
                )
            except User.DoesNotExist:
                return None
            return user
        except Exception as e:
            pass
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

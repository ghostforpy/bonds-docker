from django.contrib.auth import authenticate
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

from ..utils import parse_request


class AuthenticationTelegramChatMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            try:
                tg_body = parse_request(request)
                request.tg_body = tg_body
                request.user = authenticate(tg_body) or AnonymousUser()
            except:
                request.user = AnonymousUser()

import os
from django import template
from django.urls import reverse
#from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.simple_tag
def tg_bot_name():
    return os.getenv("TELEGRAM_BOT_NAME", False)


@register.filter(name='tg_auth_url_redirect')
def tg_auth_url_redirect(request):
    return request.build_absolute_uri(reverse('tgbot:telegram_login'))

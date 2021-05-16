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


@register.filter()
def tg_url(url):
    return url.replace('/', '_').replace('_', '/', 1)


@register.simple_tag
def today_price(security):
    currency = security.main_board_faceunit.replace(
        'РУБ', 'RUB').replace('SUR', 'RUB')
    currency = currency.replace('RUB', '₽').replace(
        'USD', '$').replace('EUR', '€')
    return '{} {}'.format(
        float("{0:.2f}".format(security.today_price)), currency
    )


@register.simple_tag
def security_history_tg_url(security):
    if security.id:
        return '/security_{}_history_'.format(security.id)
    else:
        return '/security_new_{}_history_'.format(security.isin)

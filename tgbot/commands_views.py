from django.core.cache import caches
from django.template.loader import render_to_string

from .available_commands import AVAILABLE_COMMANDS

cache = caches['default']
modes = {
    'search': 'Установлен режим поиска ценных бумаг. Введите ISIN, SECID, код, наименование....'
}


def start(request, bot=None):
    msg = render_to_string('tgbot/start_page.html', context={
        'commands': AVAILABLE_COMMANDS
    })
    bot.send_message(
        msg,
        request.tg_body.chat.id
    )


def help(request, bot=None):
    print('handle help')


def config(request, bot=None):
    print('handle config')


def getmode(request, bot=None):
    chat_id = request.tg_body.chat.id
    mode = cache.get('tgbot_{}_mode'.format(chat_id))
    if mode:
        msg = modes[mode]
    else:
        msg = 'Режим не установлен.'
    bot.send_message(
        msg,
        request.tg_body.chat.id
    )


def search(request, bot):
    chat_id = request.tg_body.chat.id
    cache.add('tgbot_{}_mode'.format(chat_id), 'search', timeout=3 * 60)
    bot.send_message(
        modes['search'],
        request.tg_body.chat.id
    )

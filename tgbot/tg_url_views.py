from django.template.loader import render_to_string

from moex.iss_simple_main import history
from moex.utils import (prepare_new_security_api,
                        get_security_in_db_by_id,
                        get_new_security_history_api,
                        get_security_in_db_history_from_moex)
from .utils import get_msg_and_buttons_security_history
from .types_classes import InlineKeyboard, InlineKeyboardButton


def send_msg_security_detail(request, bot, security):
    msg = render_to_string('tgbot/detail_security.html',
                           context={
                               'security': security
                           })
    bot.send_message(
        msg,
        chat_id=request.tg_body.chat.id,
    )


def get_security_detail(request, bot, id):
    security = get_security_in_db_by_id(id)
    send_msg_security_detail(request, bot, security)


def get_new_security_detail(request, bot, isin):
    security = prepare_new_security_api(isin)
    if security:
        send_msg_security_detail(request, bot, security)
    else:
        bot.send_message(
            'Ценная бумага не найдена. Повторите поиск.',
            chat_id=request.tg_body.chat.id,
        )


def get_security_history(request, bot, id):
    security = get_security_in_db_by_id(id)
    msg, buttons = get_msg_and_buttons_security_history(
        security, page_number=1, base=True
    )
    bot.send_message(
        msg,
        chat_id=request.tg_body.chat.id,
        reply_markup=InlineKeyboard([buttons]).to_json()

    )


def get_new_security_history(request, bot, isin):
    security = prepare_new_security_api(isin)
    if security:
        msg, buttons = get_msg_and_buttons_security_history(
            security, page_number=1, base=False
        )
        bot.send_message(
            msg,
            chat_id=request.tg_body.chat.id,
            reply_markup=InlineKeyboard([buttons]).to_json()

        )
    else:
        bot.send_message(
            'Ценная бумага не найдена. Повторите поиск.',
            chat_id=request.tg_body.chat.id,
        )

from django.template.loader import render_to_string
from django.core.paginator import Paginator

from moex.utils import prepare_new_security_api, get_security_in_db_by_id


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

from django.core.cache import caches

from moex.utils import get_security_in_db_by_id, prepare_new_security_api

from ..messages.message_views import prepare_search_msg
from ..types_classes import InlineKeyboard, InlineKeyboardButton
from ..utils import get_msg_and_buttons_security_history

cache = caches['default']


def search_callback_handle(request, bot):
    query = request.tg_body.data.split(':')[1].split('=')[1]
    page_number = request.tg_body.data.split(':')[2].split('=')[1]
    message_id = request.tg_body.message.message_id
    base = request.tg_body.data.split(':')[3].split('=')[1]
    msg, buttons, _ = prepare_search_msg(query,
                                         base=base,
                                         page_number=page_number)
    bot.edit_message_text(
        msg,
        chat_id=request.tg_body.message.chat.id,
        message_id=message_id,
        reply_markup=InlineKeyboard([buttons]).to_json()
    )


def security_history_callback_handle(request, bot):
    id = request.tg_body.data.split(':')[1].split('=')[1]
    page_number = request.tg_body.data.split(':')[2].split('=')[1]
    message_id = request.tg_body.message.message_id
    base = request.tg_body.data.split(':')[3].split('=')[1]
    if base == 'True':
        security = get_security_in_db_by_id(id)
    else:
        security = prepare_new_security_api(id)
        if not security:
            return bot.send_message(
                'Ценная бумага не найдена. Повторите поиск.',
                chat_id=request.tg_body.chat.id,
            )
    msg, buttons = get_msg_and_buttons_security_history(
        security, page_number=page_number, base=base
    )
    bot.edit_message_text(
        msg,
        chat_id=request.tg_body.message.chat.id,
        message_id=message_id,
        reply_markup=InlineKeyboard([buttons]).to_json()
    )


mode_callback_func = {
    'search': search_callback_handle,
    'security_history': security_history_callback_handle
}


def main_callback_handle(request, bot):
    try:
        get_mode = request.tg_body.data.split(':')[0].split('=')[1]

        """    chat_id = request.tg_body.message.chat.id
            mode = cache.get('tgbot_{}_mode'.format(chat_id))
            if mode == get_mode:
                cache.add('tgbot_{}_mode'.format(chat_id),
                        mode, timeout=3 * 60)
        """
        return mode_callback_func[get_mode](request, bot)
    except Exception as e:
        bot.answer_callback_query(message='oooops...something went wrong....',
                                  callback_query_id=request.tg_body.id)

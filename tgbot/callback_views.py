from django.core.cache import caches

from moex.utils import get_security_in_db_by_id
from .message_views import prepare_search_msg
from .types_classes import InlineKeyboard, InlineKeyboardButton
from .utils import get_msg_and_buttons_security_history

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
    security = get_security_in_db_by_id(id)
    msg, buttons = get_msg_and_buttons_security_history(
        security, page_number=page_number
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
    get_mode = request.tg_body.data.split(':')[0].split('=')[1]

    """    chat_id = request.tg_body.message.chat.id
        mode = cache.get('tgbot_{}_mode'.format(chat_id))
        if mode == get_mode:
            cache.add('tgbot_{}_mode'.format(chat_id),
                    mode, timeout=3 * 60)
    """
    return mode_callback_func[get_mode](request, bot)

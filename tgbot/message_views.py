import re

from django.core.cache import caches
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from moex.utils import (search_new_securities_api,
                        security_search_in_db,
                        add_search_securities_to_cache)

from .types_classes import InlineKeyboard, InlineKeyboardButton

cache = caches['default']


def prepare_search_msg(query, base='True', page_number=1):
    # base = 'True' if search in own base, 'Fasle' for new securities
    if base == 'True':
        securities = security_search_in_db(query)
        count = securities.count()
    else:
        securities = search_new_securities_api(query)
        add_search_securities_to_cache(securities)
        count = len(securities)
    paginator = Paginator(securities, 3)
    page = paginator.get_page(page_number)
    buttons = list()
    if page.has_previous():
        buttons.append(InlineKeyboardButton(
            'Prev',
            callback_data='mode={}:query={}:page={}:base={}'.format(
                'search', query, page.previous_page_number(), base
            )
        ))
    if page.has_next():
        buttons.append(InlineKeyboardButton(
            'Next',
            callback_data='mode={}:query={}:page={}:base={}'.format(
                'search', query, page.next_page_number(), base
            )
        ))
    msg = render_to_string('tgbot/search_securities.html',
                           context={
                               'base': base,
                               'query': query,
                               'page': page,
                               'pages': paginator.num_pages,
                               'count': count
                           })
    return msg, buttons, count


def search_mode(request, bot):
    query = request.tg_body.text
    match = re.findall(r'[^A-Za-zА-Яа-я0-9]{1}', query)
    empty = True
    if match:
        return bot.send_message(
            'Недопустимые символы: "{}"'.format(''.join(set(match))),
            request.tg_body.chat.id
        )
    msg, buttons, count = prepare_search_msg(query, base='True')
    if count > 0:
        empty = False
        bot.send_message(
            msg,
            request.tg_body.chat.id,
            reply_markup=InlineKeyboard([buttons]).to_json()
        )
    msg, buttons, count = prepare_search_msg(query, base='False')
    if count > 0:
        empty = False
        bot.send_message(
            msg,
            request.tg_body.chat.id,
            reply_markup=InlineKeyboard([buttons]).to_json()
        )
    if empty:
        bot.send_message(
            'По вашему запросу ничего не найдено.',
            request.tg_body.chat.id
        )


modes_views = {
    'search': search_mode
}


def main_message_handle(request, bot):
    chat_id = request.tg_body.chat.id
    # check mode
    mode = cache.get('tgbot_{}_mode'.format(chat_id))
    if mode:
        cache.add('tgbot_{}_mode'.format(chat_id),
                  mode, timeout=3 * 60)
        return modes_views[mode](request, bot)
    else:
        bot.send_message(
            'Пожалуйста, выберите режим...',
            chat_id
        )


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


mode_callback_func = {
    'search': search_callback_handle
}


def main_callback_handle(request, bot):
    get_mode = request.tg_body.data.split(':')[0].split('=')[1]
    chat_id = request.tg_body.message.chat.id
    mode = cache.get('tgbot_{}_mode'.format(chat_id))
    if mode == get_mode:
        cache.add('tgbot_{}_mode'.format(chat_id),
                  mode, timeout=3 * 60)
        return mode_callback_func[mode](request, bot)

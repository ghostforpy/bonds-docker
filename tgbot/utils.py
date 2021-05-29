import json
from datetime import datetime

from django.template.loader import render_to_string
from django.core.paginator import Paginator

from moex.api.views import History
from moex.utils import (get_new_security_history_api,
                        get_security_in_db_history_from_moex)

from .classes import Message, CallbackQuery
from .types_classes import InlineKeyboard, InlineKeyboardButton


def parse_request(request):
    t_data = json.loads(request.body)
    keys = t_data.keys()
    if 'message' in keys:
        t_message = t_data.get('message')
        return Message(**t_message)
    elif 'callback_query' in keys:
        t_callback_query = t_data.get('callback_query')
        return CallbackQuery(**t_callback_query)
    return None


def get_security_history_paginator(security):
    if security.id:
        result_history = get_security_in_db_history_from_moex(
            security,
            None,
            datetime.now().date()
        )
    else:
        result_history = get_new_security_history_api(security.isin)
    result_history = [
        History(i, result_history[i]) for i in result_history
    ]
    paginator = Paginator(result_history, 10)
    return paginator


def get_msg_and_buttons_security_history(security, page_number, base):
    paginator = get_security_history_paginator(security)
    history = paginator.get_page(page_number)
    msg = render_to_string('tgbot/security_history.html',
                           context={
                               'security': security,
                               'history': history
                           })
    buttons = list()
    if history.number > 10:
        buttons.append(InlineKeyboardButton(
            '-10',
            callback_data='mode={}:id={}:page={}:base={}'.format(
                'security_history', security.id or security.isin,
                history.number - 10, base
            )
        ))
    if history.has_previous():
        buttons.append(InlineKeyboardButton(
            'Prev',
            callback_data='mode={}:id={}:page={}:base={}'.format(
                'security_history', security.id or security.isin,
                history.previous_page_number(), base
            )
        ))
    if history.has_next():
        buttons.append(InlineKeyboardButton(
            'Next',
            callback_data='mode={}:id={}:page={}:base={}'.format(
                'security_history', security.id or security.isin, history.next_page_number(), base
            )
        ))
    if paginator.num_pages - history.number > 10:
        buttons.append(InlineKeyboardButton(
            '+10',
            callback_data='mode={}:id={}:page={}:base={}'.format(
                'security_history', security.id or security.isin, history.number + 10, base
            )
        ))
    return msg, buttons

import json

from .classes import Message, CallbackQuery


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

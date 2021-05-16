import json


class InlineKeyboardButton:
    """
    This object represents one button of an inline keyboard.
    You must use exactly one of the optional fields.
    """

    def __init__(self,
                 text: str,
                 url: str = None,
                 callback_data: str = None,
                 *args, **kwargs):
        self.text = text
        if url and callback_data:
            raise Exception
        else:
            self.url = url
            self.callback_data = callback_data

    def to_json(self):
        t = {'text': self.text}
        if self.url:
            t['url'] = self.url
        else:
            t['callback_data'] = self.callback_data
        return t


class InlineKeyboard:
    """
    Array of button rows,
    each represented by an Array of InlineKeyboardButton objects
    """

    def __init__(self,
                 rows: list,
                 *args, **kwargs):
        if not isinstance(rows, list):
            raise Exception
        for i in rows:
            if not isinstance(i, list):
                raise Exception
            for j in i:
                if not isinstance(j, InlineKeyboardButton):
                    raise Exception
        self.rows = rows

    def to_json(self):
        t = json.dumps({
            'inline_keyboard':
            [[j.to_json() for j in i] for i in self.rows]
        })
        return t

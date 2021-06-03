#import json
import re
import uuid
from typing import List

from pydantic import BaseModel

#from django.core.cache import caches
from django.template.loader import render_to_string
from django.core.paginator import Paginator

from moex.utils import (search_new_securities_api,
                        security_search_in_db,
                        add_search_securities_to_cache)

from ..classes import InlineQueryResultArticle, InputTextMessageContent

#cache = caches['default']


class InputTextMessageContent(BaseModel):
    message_text: str
    parse_mode = 'html'


class InlineQueryResultArticle(BaseModel):
    type = 'article'
    id: str
    title: str = None
    input_message_content: InputTextMessageContent = None


class Results(BaseModel):
    __root__: List[InlineQueryResultArticle]


def main_inline_query_handle(request, bot):
    inline_query = request.tg_body
    page_number = inline_query.offset or 1
    query_id = inline_query.id
    query = inline_query.query
    #print(query_id, query, page_number)
    match = re.findall(r'[^A-Za-zА-Яа-яёЁ0-9]{1}', query)
    if query != '' and not match:
        securities_in_db = security_search_in_db(query)
        new_securities = search_new_securities_api(query)
        add_search_securities_to_cache(new_securities)
        securities = list(securities_in_db) + new_securities
    else:
        securities = security_search_in_db('')

    paginator = Paginator(securities, 3)
    page = paginator.get_page(page_number)
    results = [
        InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=i.shortname,
            input_message_content=InputTextMessageContent(
                message_text=render_to_string('tgbot/detail_security_inlinequery_mode.html',
                                              context={
                                                  'security': i
                                              })
            )
        ) for i in page
    ]
    next_offset = page.next_page_number() if page.has_next() else ''
    bot.answer_inline_query(query_id,
                            Results(__root__=results).json(),
                            next_offset=next_offset)

#!/usr/bin/env python
from lxml import html
import requests
from datetime import datetime, timedelta, date


def rshb_history(url,
                 date_since=datetime.now().date() - timedelta(31),
                 date_until=datetime.now().date()):
    if isinstance(date_since, str):
        date_since = datetime.strptime(date_since, '%d.%m.%Y').date()
    if isinstance(date_until, str):
        date_until = datetime.strptime(date_since, '%d.%m.%Y').date()
    url = url
    page = requests.get(url)
    page1 = html.document_fromstring(page.content)
    id = 'period_all'
    e = page1.get_element_by_id(id)
    table = e.getchildren()[0].findall('tbody').pop()
    table_history = {}
    for i in range(len(table)):
        date = datetime.strptime(table[i][0].text, '%d.%m.%Y').date()
        if date_since <= date <= date_until:
            price = float(table[i][1].text.replace(r' ', ''))
            table_history[date] = price
    return table_history


urls = {'bestind': 'https://rshb-am.ru/trust/bestind/',
        'share': 'https://rshb-am.ru/trust/share/',
        'balanced': 'https://rshb-am.ru/trust/balanced/',
        'treasury': 'https://rshb-am.ru/trust/treasury/',
        'CurBonds': 'https://rshb-am.ru/trust/CurBonds/',
        'bonds': 'https://rshb-am.ru/trust/bonds/',
        'gold': 'https://rshb-am.ru/trust/gold/'}
PIF_names = {'bestind':
             'ОПИФ рыночных финансовых инструментов «РСХБ – Лучшие отрасли»',
             'share':
             'ОПИФ рыночных финансовых инструментов «РСХБ – Фонд Акций»',
             'balanced':
             'ОПИФ рыночных финансовых инструментов «РСХБ – Фонд Сбалансированный»',
             'treasury':
             'ОПИФ рыночных финансовых инструментов «РСХБ – Казначейский»',
             'CurBonds':
             'ОПИФ рыночных финансовых инструментов «РСХБ – Валютные облигации»',
             'bonds':
             'ОПИФ рыночных финансовых инструментов «РСХБ - Фонд Облигаций»',
             'gold':
             'ОПИФ рыночных финансовых инструментов «РСХБ – Золото, серебро, платина»'}


if __name__ == '__main__':
    # for i in urls[0:1]:
    print(rshb_history(urls['bestind'],
        datetime(2020, 4, 1).date(),
        datetime(2020, 5, 1).date()))

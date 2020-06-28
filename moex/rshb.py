#!/usr/bin/env python
from lxml import html
import requests
from datetime import datetime, timedelta
import re


def rshb(url, date=datetime.now(), first=False):
    url = url
    page = requests.get(url)
    tree = html.fromstring(page.content)
    xpath = '//td[@align = "right"]'
    element = tree.xpath(xpath)[0]
    # get date publication
    if element.text.replace(r' ', '') == 'Опубликовано:':
        elem = element.xpath('.//strong')[0]
        date_publication = elem.text.split()[0]
        date_publication = datetime.strptime(date_publication,
                                             '%d.%m.%Y').date()
    # get information
    # print(date_publication)
    # print(date)
    if first or date_publication >= date:
        xpath = '//td[@class = "content left"]'
        element = tree.xpath(xpath)[0]
        elements = element.xpath('.//td')
        date_today = elements[0].text
        price_today = elements[1].text[:-5].replace(r' ', '')
        date_prev = elements[2].text
        price_prev = elements[3].text[:-5].replace(r' ', '')
        result = {'date_today':
                  datetime.strptime(date_today, '%d.%m.%Y').date(),
                  'price_today':
                  float(price_today),
                  'date_prev':
                  datetime.strptime(date_prev, '%d.%m.%Y').date(),
                  'price_prev':
                  float(price_prev),
                  'date_publication': date_publication}
        return result
    else:
        return False


def rshb_history(url,
                 date_since=datetime.now().date() - timedelta(31),
                 date_until=datetime.now().date(),
                 format_result='date'):
    if isinstance(date_since, str):
        date_since = datetime.strptime(date_since, '%d.%m.%Y').date()
    if isinstance(date_until, str):
        date_until = datetime.strptime(date_since, '%d.%m.%Y').date()
    '''    if date_since is None:
        date_since = datetime.now().date() - timedelta(31)
    if date_until is None:
        date_until = datetime.now().date()
        '''
    url = url
    page = requests.get(url)
    page1 = html.document_fromstring(page.content)
    id = 'period_all'
    e = page1.get_element_by_id(id)
    table = e.getchildren()[0].findall('tbody').pop()
    table_history = {}
    #print(date_since, date_until)
    for i in range(len(table)):
        date = datetime.strptime(table[i][0].text, '%d.%m.%Y').date()
        try:
            if date_since >= date or date >= date_until:
                continue
                #price = re.sub(r'[^\d\.]', "", table[i][1].text)
                #table_history[date] = price
        except TypeError:
            pass
        price = re.sub(r'[^\d\.]', "", table[i][1].text)
        if format_result != 'date':
            date = table[i][0].text
        table_history[date] = price
    return table_history


urls = {'bestind': 'https://rshb-am.ru/trust/bestind/',
        'share': 'https://rshb-am.ru/trust/share/',
        'balanced': 'https://rshb-am.ru/trust/balanced/',
        'treasury': 'https://rshb-am.ru/trust/treasury/',
        'CurBonds': 'https://rshb-am.ru/trust/CurBonds/?CURR=RUB',
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
    for i in urls:
        print(PIF_names[i],
              urls[i],
              rshb(urls[i]),
              sep='\n')
        history = rshb_history(urls[i])
        for j in history:
            print(j, history[j])

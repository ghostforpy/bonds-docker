import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.core.cache import caches


def get_cbr_xml_daily_curses(date=None):
    """
    date:datetime.date()
    """
    if not date:
        date = datetime.now().date()
    str_date = date.strftime('%d.%m.%Y').split('.')
    if not caches['default'].get('daily_curses_' + '.'.join(str_date)):
        url = 'https://www.cbr.ru/scripts/XML_daily.asp?date_req={}/{}/{}'\
            .format(*str_date)
        try:
            r = requests.get(url)
        except:
            return None
        root = ET.fromstring(r.text)
        result = dict()
        for valute in root.findall('Valute'):
            code_id = valute.get('ID')
            char_code = valute.find('CharCode').text
            num_code = valute.find('NumCode').text
            value = float(valute.find('Value').text.replace(',', '.')) / float(valute.find('Nominal').text)
            name = valute.find('Name').text
            result[char_code] = {'Value': value,
                                 'Name': name,
                                 'NumCode': num_code,
                                 'ID': code_id
                                 }
        caches['default'].add('daily_curses_' + '.'.join(str_date),
                              result,
                              timeout=10 * 60 * 60)
    else:
        result = caches['default'].get('daily_curses_' + '.'.join(str_date))
    return {'Date': '.'.join(str_date), 'ValCurs': result}


def get_valute_curse(valute, date=None):
    data = get_cbr_xml_daily_curses(date)
    return data['ValCurs'][valute]['Value']


def refresh_valute_curse(valute, date=None):
    data = get_cbr_xml_daily_curses(date)
    return [data['ValCurs'][valute]['Value'], data['Date']]


def get_valute_code(valute):
    data = get_cbr_xml_daily_curses()
    return data['ValCurs'][valute]['ID']


def get_valute_history(valute, date_since=None, date_until=None):
    if date_until is None:
        date_until = datetime.now().date()
    if date_since is None:
        date_since = date_until - timedelta(days=365)
    data = get_cbr_xml_daily_curses()
    code_id = get_valute_code(valute)
    date_since = date_since.strftime('%d/%m/%Y')
    date_until = date_until.strftime('%d/%m/%Y')
    url = 'https://www.cbr.ru/scripts/XML_dynamic.asp?'
    url += 'date_req1={}&date_req2={}&VAL_NM_RQ={}'\
        .format(date_since, date_until, code_id)
    try:
        r = requests.get(url)
    except:
        return None
    root = ET.fromstring(r.text)
    result = dict()
    for record in root.findall('Record'):
        date = record.get('Date')
        nominal = record.get('Nominal')
        value = float(record.find('Value').text.replace(',', '.')) / float(nominal)
        result[date] = str(value)
    return result

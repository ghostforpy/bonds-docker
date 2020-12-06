from datetime import datetime, date
import yfinance as yf


class NoSecurityYFinance(Exception):
    pass


class NoSecurityYFinanceHistory(Exception):
    pass


def search_in_yfinance(query, raise_exceptions=False):
    try:
        q = yf.Ticker(query)
        info = q.info
    except KeyError:
        if raise_exceptions:
            raise NoSecurityYFinance
        else:
            return None
    try:
        isin = q.isin
    except:
        isin = None
    return {
        'shortname': info['shortName'],
        'name': info['symbol'],
        'emitent': info['longName'],
        'isin': isin
    }


def get_security_yfinance(secid, raise_exceptions=True):
    try:
        q = yf.Ticker(secid)
        info = q.info
    except KeyError:
        if raise_exceptions:
            raise NoSecurityYFinance
        else:
            return None
    try:
        isin = q.isin
    except:
        isin = None
    url = 'https://finance.yahoo.com/quote/{}/profile?p={}'.\
        format(secid, secid)
    return {
        'name': info['shortName'],
        'url': url,
        'security_type': 'share',
        'shortname': info['shortName'],
        'fullname': info['longName'],
        'secid': info['symbol'],
        'isin': isin,
        'emitent': info['shortName'],
        'faceunit': info['currency'],
        'main_board_faceunit': info['currency'],
        'today_price': info['previousClose'],
        'website': info['website']
    }


def get_history_by_secid(secid, period=None, start=None, end=None):
    kwargs = dict()
    if isinstance(end, datetime):
        kwargs['end'] = end
    if isinstance(start, datetime):
        kwargs['start'] = start
    if start is None or not isinstance(period, str):
        kwargs['period'] = '2y'
    try:
        q = yf.Ticker(secid)
        history = q.history(**kwargs)
        history_close = history['Close'].to_dict()
        return {
            datetime.fromtimestamp(datetime.timestamp(i)).date():
            history_close[i]
            for i in history_close
        }
    except KeyError:
        if raise_exceptions:
            raise NoSecurityYFinanceHistory
        else:
            return None

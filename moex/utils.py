import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date
import threading
from decimal import Decimal
from django.core.cache import caches
from django.core.exceptions import (PermissionDenied,
                                    ObjectDoesNotExist)
from django.db.models import Q
from .iss_simple_main import (search as moex_search,
                              specification as moex_specification,
                              history as moex_history,
                              NoSecurityMoex)
from .models import Security
from .utils_valute import get_valute_curse as g_v_c
from .utils_yfinance import (search_in_yfinance,
                             NoSecurityYFinance,
                             get_security_yfinance,
                             get_history_by_secid)

get_valute_curse = g_v_c


def get_securities_in_portfolios_by_user(user):
    qs = user.securities.all().prefetch_related('security')
    return [i.security for i in qs]


def get_followed_securities_by_user(user, exclude_portfolios=True):
    result = user.security_followed.all()
    if exclude_portfolios:
        security_in_portfolios = user.securities.all().values('security')
        result = result.exclude(id__in=security_in_portfolios)
    return result


def upload_history(security):
    cache = caches['default']
    security_history = security.get_history(None,
                                            None,
                                            format_result='str')
    cache.add('security_history_by_id' + str(security.id),
              security_history, timeout=30)
    return security_history


def staff_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner


def upload_search_moex_to_cache(query):
    # not used
    cache = caches['default']
    result = moex_search(query)
    securities = Security.objects.all()
    secids = [i.secid for i in securities]
    # delete securities if exist in base
    res = {i: result[i] for i in result if i not in secids}
    cache.add('moex_search_' + query,
              res, timeout=24 * 60 * 60)


def prepare_new_security_by_secid_on_moex(secid):
    description, boards = moex_specification(secid)
    if not caches['default'].get('moex_secid_' + description["SECID"]):
        data = boards['data']
        board = description['primary_boardid']
        for i in data:
            if i[1] == board:
                engine = i[7]
                market = i[5]
                break
        if re.search(r'bond', description["TYPE"]):
            security_type = 'bond'
        elif re.search(r'etf_ppif', description["TYPE"]):
            security_type = 'etf_ppif'
        elif re.search(r'ppif', description["TYPE"]):
            security_type = 'ppif'
        elif re.search(r'share', description["TYPE"]):
            security_type = 'share'
        elif re.search(r'futures', description["TYPE"]):
            security_type = 'futures'
        elif re.search(r'index', description["TYPE"]):
            security_type = 'index'
        elif re.search(r'depositary_receipt', description["TYPE"]):
            security_type = 'depositary_receipt'
        else:
            pass
        regnumber = get_value(description, "REGNUMBER")
        isin = get_value(description, "ISIN")
        facevalue = get_value(description, "FACEVALUE", 0)
        issuesize = get_value(description, "ISSUESIZE", 0)
        initialfacevalue = get_value(description, "INITIALFACEVALUE", 0)
        matdate = get_value(description, "MATDATE")
        coupondate = get_value(description, "COUPONDATE")
        couponfrequency = get_value(description, "COUPONFREQUENCY")
        couponpercent = get_value(description, "COUPONPERCENT")
        couponvalue = get_value(description, "COUPONVALUE")
        faceunit = get_value(description, "FACEUNIT")
        main_board_faceunit = get_value(description, "MAINBOARDFACEUNIT")
        url = 'https://www.moex.com/ru/issue.aspx?code=' + description["SECID"]
        parce_url = 'http://iss.moex.com/iss/history/engines/' + \
            '{}/markets/{}/'.format(engine, market) + \
            'boards/{}/securities/{}.json'.format(board, description["SECID"])
        today_price, last_update, accint, change_price_percent = upload_moex_history(
            parce_url, description["SECID"], security_type, facevalue)
        newitem = Security(fullname=description["NAME"],
                           shortname=description["SHORTNAME"],
                           name=description["SHORTNAME"],
                           regnumber=regnumber,
                           secid=description["SECID"],
                           isin=isin,
                           facevalue=facevalue,
                           initialfacevalue=initialfacevalue,
                           matdate=matdate,
                           security_type=security_type,
                           url=url,
                           emitent=description['emitent'],
                           board=board,
                           engine=engine,
                           market=market,
                           parce_url=parce_url,
                           coupondate=coupondate,
                           couponfrequency=couponfrequency,
                           couponpercent=couponpercent,
                           couponvalue=couponvalue,
                           accint=accint,
                           faceunit=faceunit,
                           issuesize=issuesize,
                           main_board_faceunit=main_board_faceunit,
                           oldest_date=datetime.now().date(),
                           today_price=today_price,
                           last_update=last_update,
                           change_price_percent=change_price_percent,
                           source='moex')
        caches['default'].add('moex_secid_' + description["SECID"],
                              newitem, timeout=60 * 60)
    else:
        newitem = caches['default'].get('moex_secid_' + description["SECID"])
    return newitem


def upload_history_yfinance_to_cache(secid):
    history = get_history_by_secid(secid)
    caches['default'].add('yfinance_security_history_secid_' + secid,
                          history, timeout=60 * 60)


def prepare_new_security_by_secid_yfinance(secid):
    if not caches['default'].get('yfinance_secid_' + secid):
        new = get_security_yfinance(secid)
        newitem = Security(
            source='yfinance',
            last_update=datetime.now().date(),
            oldest_date=datetime.now().date(),
            **new)
        caches['default'].add('yfinance_secid_' + secid,
                              newitem, timeout=60 * 60)
    else:
        newitem = caches['default'].get('yfinance_secid_' + secid)
    if not caches['default'].get('yfinance_security_history_secid_' + secid):
        # блок кеширования исторических данных поценной бумаге
        # для дальнейшей загрузки через ajax-запрос
        t = threading.Thread(target=upload_history_yfinance_to_cache, args=(secid,))
        t.start()
        # конец блока кеширования
    return newitem


def prepare_new_security_by_secid(secid):
    try:
        newitem = prepare_new_security_by_secid_on_moex(secid)
    except NoSecurityMoex:
        newitem = None
    if newitem is None:
        try:
            newitem = prepare_new_security_by_secid_yfinance(secid)
        except NoSecurityYFinance:
            newitem = None
    return newitem


def get_value(dictionary, key, default=None):
    try:
        result = dictionary[key]
        if key in ["MATDATE", "COUPONDATE"]:
            result = datetime.strptime(result, '%Y-%m-%d').date()
        return result
    except KeyError:
        return default


def upload_moex_history(parce_url, secid, security_type, facevalue):
    security_history = moex_history(parce_url)
    if security_type == 'bond':
        for i in security_history:
            try:
                security_history[i]['CLOSE'] = str(
                    float(security_history[i]['CLOSE']) * float(facevalue
                                                                ) / 100)
            except Exception:
                pass
                # security_history.pop(i)
    days = sorted(
        security_history,
        key=lambda i: datetime.strptime(i, '%d.%m.%Y').date(),
        reverse=True)
    result_history = {i: security_history[i]['CLOSE'] for i in days}
    caches['default'].add('moex_security_history_secid' + secid,
                          result_history, timeout=60 * 60)
    today_price = security_history[days[0]]['CLOSE']
    try:
        previos_price = security_history[days[1]]['CLOSE']
        change_price_percent = (float(today_price) - float(previos_price))\
            / float(previos_price) * 100
        change_price_percent = float("{0:.2f}".format(change_price_percent))
    except Exception:
        change_price_percent = 0
    try:
        accint = security_history[days[0]]['ACCINT']
    except KeyError:
        accint = None
    return today_price,\
        datetime.strptime(days[0], '%d.%m.%Y').date(),\
        accint,\
        change_price_percent


def security_search_in_db(query):
    return Security.objects.filter(
        Q(name__icontains=query) |
        Q(code__icontains=query) |
        Q(fullname__icontains=query) |
        Q(regnumber__icontains=query) |
        Q(secid__icontains=query) |
        Q(isin__icontains=query) |
        Q(emitent__icontains=query)
    ).order_by('-last_update', '-id')


def security_search_in_moex(query):
    if not caches['default'].get('moex_search_' + query):
        result = moex_search(query)
        securities = Security.objects.all()
        secids = [i.secid for i in securities]
        if result:
            # delete securities if exist in base
            res = {
                i: result[i] for i in result if re.search(
                    r'bond|etf_ppif|ppif|share|futures|index|depositary_receipt',
                    result[i]['type']
                )
            }
            res = {i: res[i] for i in res if i not in secids}
        else:
            res = dict()
        result_yfinance = search_in_yfinance(query)
        if result_yfinance:
            if query not in secids:
                res[result_yfinance['name']] = result_yfinance
        if res:
            caches['default'].add('moex_search_' + query,
                                  res, timeout=24 * 60 * 60)
    else:
        res = caches['default'].get('moex_search_' + query)
    return res


def get_new_security_type(security_type):
    if re.search(r'bond', security_type):
        return 'bond'
    elif re.search(r'etf_ppif', security_type):
        return 'etf_ppif'
    elif re.search(r'ppif', security_type):
        return 'ppif'
    elif re.search(r'share', security_type):
        return 'share'
    elif re.search(r'futures', security_type):
        return 'futures'
    elif re.search(r'index', security_type):
        return 'index'
    elif re.search(r'depositary_receipt', security_type):
        return 'depositary_receipt'


class NewSearchSecurity:
    def __init__(self,
                 secid,
                 isin,
                 shortname,
                 name,
                 emitent,
                 source,
                 security_type,
                 query: str = None,
                 **kwargs):
        self.secid = secid
        self.isin = isin
        self.shortname = shortname
        self.name = name
        self.emitent = emitent
        self.source = source
        self.security_type = security_type
        self.query = query


def search_new_securities_api(query):
    if not caches['default'].get('moex_search_api_' + query):
        result_moex = moex_search(query)
        securities = Security.objects.all()
        secids = [i.secid.upper() for i in securities if i.secid]
        if result_moex:
            # delete securities if exist in base
            temp = {
                i: result_moex[i] for i in result_moex if re.search(
                    r'bond|etf_ppif|ppif|share|futures|index|depositary_receipt',
                    result_moex[i]['type']
                )
            }
            temp = {i: temp[i] for i in temp if i not in secids}
            result = [
                NewSearchSecurity(
                    secid=i,
                    isin=temp[i]['isin'],
                    shortname=temp[i]['shortname'],
                    name=temp[i]['name'],
                    emitent=temp[i]['emitent'],
                    source='moex',
                    security_type=get_new_security_type(temp[i]['type']),
                    query=query
                ) for i in temp
            ]
        else:
            result = list()
        result_yfinance = search_in_yfinance(query)
        if result_yfinance:
            if query.upper() not in secids:
                result.append(
                    NewSearchSecurity(
                        secid=query.upper(),
                        isin=result_yfinance['isin'],
                        shortname=result_yfinance['shortname'],
                        source='yfinance',
                        name=result_yfinance['name'],
                        emitent=result_yfinance['emitent'],
                        security_type='share',
                        query=query
                    )
                )
        if result:
            caches['default'].add('moex_search_api_' + query,
                                  result, timeout=2 * 60 * 60)
    else:
        result = caches['default'].get('moex_search_api_' + query)
    return result


def add_search_securities_to_cache(securities):
    for i in securities:
        if caches['default'].get('new_security_' + i.isin):
            pass
        else:
            caches['default'].add('new_security_' + i.isin,
                                  i, timeout=24 * 60 * 60)


def prepare_new_security_api(isin):
    security_item = caches['default'].get('new_security_' + isin)
    if not security_item:
        return
    if security_item.source == 'moex':
        security = prepare_new_security_by_secid_on_moex(security_item.secid)
    elif security_item.source == 'yfinance':
        security = prepare_new_security_by_secid_yfinance(security_item.secid)
    return security


def delete_search_query_from_cache(isin):
    security_item = caches['default'].get('new_security_' + isin)
    if not security_item:
        return
    query = security_item.query
    caches['default'].delete('moex_search_api_' + query)


def get_new_security_history_from_moex(secid):
    if caches['default'].get('moex_secid_' + secid):
        newitem = caches['default'].get('moex_secid_' + secid)
    else:
        return {'status': 'no_secid_security'}
    result = caches['default'].get('moex_security_history_secid' + secid)
    if result is None:
        parce_url = newitem.parce_url
        result = moex_history(parce_url)
        result = {i: i['CLOSE'] for i in result}
    days = sorted(
        result,
        key=lambda i: datetime.strptime(i, '%d.%m.%Y').date(),
        reverse=True)
    result_history = {i: result[i] for i in days}
    return {'status': 'ok',
            'result_history': result_history,
            'currency': newitem.get_main_board_faceunit_display()}


def get_new_security_history_from_yfinance(secid):
    if caches['default'].get('yfinance_secid_' + secid):
        newitem = caches['default'].get('yfinance_secid_' + secid)
    else:
        return {'status': 'no_secid_security'}
    if not caches['default'].get(
            'yfinance_security_history_secid_' + secid):
        upload_history_yfinance_to_cache(secid)

    result = caches['default'].get(
        'yfinance_security_history_secid_' + secid
    )
    days = sorted(
        result,
        key=lambda i: i,
        reverse=True
    )
    result_history = {
        datetime.strftime(i, '%d.%m.%Y'): float("{0:.2f}".format(result[i]))
        for i in days
    }
    return {'status': 'ok',
            'result_history': result_history,
            'currency': newitem.get_main_board_faceunit_display()}


def get_new_security_history(secid):
    history = get_new_security_history_from_moex(secid)
    if history['status'] == 'ok':
        return history
    history = get_new_security_history_from_yfinance(secid)
    if history['status'] == 'ok':
        return history
    # если ни один метод не вернул status ok
    return {'status': 'no_secid_security'}


def get_new_security_history_api(isin):
    security_item = caches['default'].get('new_security_' + isin)
    if not security_item:
        return
    if security_item.source == 'moex':
        history = get_new_security_history_from_moex(security_item.secid)
    elif security_item.source == 'yfinance':
        history = get_new_security_history_from_yfinance(security_item.secid)
    if history['status'] == 'ok':
        return history['result_history']
    return


def get_security_in_db_history_from_moex(security, date_since, date_until):
    cache = caches['default']
    security_history = cache.get('security_history_by_id' + str(security.id))
    if not security_history:
        security_history = security.get_history(date_since,
                                                date_until,
                                                format_result='str')
        caches['default'].add('security_history_by_id' + str(security.id),
                              security_history, timeout=12 * 60 * 60)

    try:
        days = sorted(
            security_history,
            key=lambda i: datetime.strptime(i, '%d.%m.%Y').date(),
            reverse=True)
        result_history = {i: security_history[i] for i in days}
    except TypeError:
        days = sorted(
            security_history,
            key=lambda i: i,
            reverse=True)
        result_history = {
            datetime.strftime(i, '%d.%m.%Y'): float("{0:.2f}".format(
                security_history[i]))
            for i in days}
    return result_history


def get_or_prepare_new_security_by_secid(secid):
    if not caches['default'].get('moex_secid_' + secid):
        if not caches['default'].get('yfinance_secid_' + secid):
            security = prepare_new_security_by_secid(secid)
        else:
            security = caches['default'].get('yfinance_secid_' + secid)
    else:
        security = caches['default'].get('moex_secid_' + secid)
    return security


def get_today_price_by_secid(secid, day=None, ignore_bond_nkd=False):
    try:
        security = Security.objects.get(secid=secid)
        if day:
            history = get_security_in_db_history_from_moex(security)
            today_price = history[day]
        else:
            today_price = security.today_price
    except ObjectDoesNotExist:
        security = get_or_prepare_new_security_by_secid(secid)
        if not security:
            raise NoSecurityMoex
        if day:
            history = get_new_security_history(
                secid)['result_history']
            temp = {datetime.strptime(
                i, '%d.%m.%Y'): history[i] for i in history}
            today_price = temp[day]
        else:
            today_price = security.today_price
    if security.main_board_faceunit != 'SUR':
        valute = security.main_board_faceunit
        if day:
            today_price *= Decimal(get_valute_curse(valute, day))
        else:
            today_price *= Decimal(
                get_valute_curse(valute, datetime.now().date())
            )
    if security.security_type == 'bond' and not ignore_bond_nkd:
        today_nkd = (float(security.couponvalue) *
                     float(security.couponfrequency) / 365
                     )
        today_price = float(today_price) + (float(security.accint) +  # NKD
                                            today_nkd  # today NKD
                                            )
    return today_price


def get_security_by_secid(secid, return_from_db_flag=False):
    # return_from_db_flag устанавливается, если нужно знать
    # имеется ли ценная бумага в базе
    try:
        security = Security.objects.get(
            secid=secid
            #Q(secid=secid) | Q(isin=secid)
            )
        if return_from_db_flag:
            return security, True
    except (ObjectDoesNotExist, Security.DoesNotExist):
        security = get_or_prepare_new_security_by_secid(secid)
        if return_from_db_flag:
            return security, False
    return security


def get_security_in_db_by_id(id):
    try:
        security = Security.objects.get(id=id)
    except ObjectDoesNotExist:
        return None
    return security

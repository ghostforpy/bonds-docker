import re
from datetime import datetime
from django.core.cache import caches
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .iss_simple_main import search as moex_search,\
    specification as moex_specification,\
    history as moex_history
from .models import Security


def get_securities_in_portfolios_by_user(user):
    return [i.security for i in user.securities.all()]


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
    cache = caches['default']
    result = moex_search(query)
    securities = Security.objects.all()
    secids = [i.secid for i in securities]
    # delete securities if exist in base
    res = {i: result[i] for i in result if i not in secids}
    cache.add('moex_search_' + query,
              res, timeout=24 * 60 * 60)


def prepare_new_security_by_secid(secid):
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
        else:
            pass
        regnumber = get_value(description, "REGNUMBER")
        isin = get_value(description, "ISIN")
        facevalue = get_value(description, "FACEVALUE", 0)
        initialfacevalue = get_value(description, "INITIALFACEVALUE", 0)
        matdate = get_value(description, "MATDATE")
        coupondate = get_value(description, "COUPONDATE")
        couponfrequency = get_value(description, "COUPONFREQUENCY")
        couponpercent = get_value(description, "COUPONPERCENT")
        couponvalue = get_value(description, "COUPONVALUE")
        faceunit = get_value(description, "FACEUNIT")
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
                           oldest_date=datetime.now().date(),
                           today_price=today_price,
                           last_update=last_update,
                           change_price_percent=change_price_percent)
        caches['default'].add('moex_secid_' + description["SECID"],
                              newitem, timeout=60 * 60)
    else:
        newitem = caches['default'].get('moex_secid_' + description["SECID"])
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
    )


def security_search_in_moex(query):
    if not caches['default'].get('moex_search_' + query):
        result = moex_search(query)
        securities = Security.objects.all()
        secids = [i.secid for i in securities]
        # delete securities if exist in base
        res = {i: result[i] for i in result if i not in secids}
        if res:
            caches['default'].add('moex_search_' + query,
                                  res, timeout=24 * 60 * 60)
    else:
        res = caches['default'].get('moex_search_' + query)
    return res


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
    return {'status': 'ok', 'result_history': result_history}


def get_security_in_db_history_from_moex(security, date_since, date_until):
    cache = caches['default']
    security_history = cache.get('security_history_by_id' + str(security.id))
    if not security_history:
        security_history = security.get_history(date_since,
                                                date_until,
                                                format_result='str')
    days = sorted(
        security_history,
        key=lambda i: datetime.strptime(i, '%d.%m.%Y').date(),
        reverse=True)
    result_history = {i: security_history[i] for i in days}
    return result_history


def get_today_price_by_secid(secid, day=None):
    if not caches['default'].get('moex_secid_' + secid):
        prepare_new_security_by_secid(secid)
    history = get_new_security_history_from_moex(secid)['result_history']
    temp = {datetime.strptime(i, '%d.%m.%Y'): history[i] for i in history}
    if day:
        today_price = temp[day]
    else:
        max_day = max(temp.keys())
        today_price = temp[max_day]
    return today_price

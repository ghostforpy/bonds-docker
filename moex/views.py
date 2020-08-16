from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.core.cache import caches
import threading
import re
from django.core.mail import send_mail
from .models import *
from .forms import *
from .iss_simple_main import search as moex_search,\
    specification as moex_specification,\
    history as moex_history
# Create your views here.


#@cache_page(60 * 60)
def upload_history(security):
    cache = caches['default']
    security_history = security.get_history(None,
                                            None,
                                            format_result='str')
    cache.add('security_history_by_id' + str(security.id),
              security_history, timeout=30)


def staff_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return function(request, *args, **kwargs)
    return _inner


@login_required
def security_detail(request, id):
    try:
        security = get_object_or_404(Security, id=id)
        security_in_user_portfolios = None
        if request.user.is_authenticated:
            user = request.user
            security_in_user_portfolios = security.portfolios.filter(
                owner=user)
        # блок кеширования
        t = threading.Thread(target=upload_history, args=(security,))
        t.start()
        # конец блока кеширования
        return render(request,
                      'moex/detail.html',
                      {'security':
                       security,
                       'security_in_user_portfolios':
                       security_in_user_portfolios})
    except ObjectDoesNotExist:
        return redirect(request.META.get('HTTP_REFERER'))


def upload_search_moex_to_cache(query):
    cache = caches['default']
    result = moex_search(query)
    securities = Security.objects.all()
    secids = [i.secid for i in securities]
    # delete securities if exist in base
    res = {i: result[i] for i in result if i not in secids}
    cache.add('moex_search_' + query,
              res, timeout=24 * 60 * 60)


def security_list(request):
    form = SearchForm()
    query = None
    moex_dict = None
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            securities_list = Security.objects.filter(
                Q(name__icontains=query) |
                Q(code__icontains=query) |
                Q(fullname__icontains=query) |
                Q(regnumber__icontains=query) |
                Q(secid__icontains=query) |
                Q(isin__icontains=query) |
                Q(emitent__icontains=query)
            )
            if caches['default'].get('moex_search_' + query):
                moex_dict = caches['default'].get('moex_search_' + query)
        else:
            securities_list = Security.objects.all()
    else:
        securities_list = Security.objects.all()
    paginator = Paginator(securities_list, 20)
    page = request.GET.get('page')
    securities = paginator.get_page(page)
    return render(request,
                  'moex/list.html',
                  {'securities': securities,
                   'moex_dict': moex_dict,
                   'form': form,
                   'query': query})


def security_search_moex(request):
    query = request.GET.get('query')
    if not query:
        return JsonResponse({'status': 'no'})
    result = {}
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
    content = {}
    if res:
        content['response'] = res
        content['status'] = 'ok'
    elif result:
        content['status'] = 'no duplicate'
    else:
        content['status'] = 'no security'
    return JsonResponse(content)


@login_required
def security_buy(request, id):
    if request.method == 'GET':
        portfolio_id = request.GET.get('portfolio')
        date = request.GET.get('date') or now().date()
        buy = True if request.GET.get('buy') == 'true' else False
        try:
            portfolio = request.user.portfolios.get(id=portfolio_id)
        #    portfolios = None
        except ObjectDoesNotExist:
            portfolio = None
        portfolios = request.user.portfolios.filter(manual=False)
        # JsonResponse({'status': 'no portfolio id'})
        try:
            security = get_object_or_404(Security, id=id)
        except ObjectDoesNotExist:
            JsonResponse({'status': 'no security id'})
        price = request.GET.get('price') or security.today_price
        newitem = TradeHistory(date=date,
                               price=price)
        form = TradeHistoryForm(instance=newitem)
        return render(request,
                      'moex/buy.html',
                      {'form': form,
                       'portfolio': portfolio,
                       'portfolios': portfolios,
                       'buy': buy,
                       'security': security})
    elif request.method == 'POST':
        form = TradeHistoryForm(request.POST)
        try:
            security = get_object_or_404(
                Security, id=id)
        except ObjectDoesNotExist:
            JsonResponse({'status': 'no security id'})
        buy = True if request.POST.get('buy') == 'true' else False
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.security = security
            new_item.owner = request.user
            new_item.buy = buy
            new_item.save()
            messages.success(request, 'Портфель успешно обновлён.')
            return redirect(new_item.portfolio.get_absolute_url())
        else:
            try:
                portfolio = request.user.portfolios.get(
                    id=request.POST.get('portfolio'))
            except ObjectDoesNotExist:
                portfolio = None
            return render(request,
                          'moex/buy.html',
                          {'form': form,
                           'portfolio': portfolio,
                           'buy': buy,
                           'security': security})
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def new_security_buy(request, secid):
    portfolios = request.user.portfolios.filter(manual=False)
    buy = True
    security = caches['default'].get('moex_secid_' + secid)
    if not security:
        return redirect(reverse('moex:list'))
    if request.method == 'GET':
        date = request.GET.get('date') or now().date()
        price = request.GET.get('price') or security.today_price
        newitem = TradeHistory(date=date,
                               price=price)
        form = TradeHistoryForm(instance=newitem)
        return render(request,
                      'moex/buy.html',
                      {'form': form,
                       'portfolios': portfolios,
                       'buy': buy,
                       'security': security,
                       'new_security': True})
    elif request.method == 'POST':
        form = TradeHistoryForm(request.POST)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.owner = request.user
            new_item.buy = buy
            security.save()
            new_item.security = security
            new_item.save()
            messages.success(request, 'Портфель успешно обновлён.')
            return redirect(new_item.portfolio.get_absolute_url())
        else:
            portfolio = form.portfolio
            return render(request,
                          'moex/buy.html',
                          {'form': form,
                           'portfolio': portfolio,
                           'portfolios': portfolios,
                           'buy': buy,
                           'security': security,
                           'new_security': True})
    return redirect(request.META.get('HTTP_REFERER'))


def get_value(dictionary, key, default=None):
    try:
        result = dictionary[key]
        if key in ["MATDATE", "COUPONDATE"]:
            result = datetime.strptime(result, '%Y-%m-%d').date()
        return result
    except KeyError:
        return default


@staff_only
@require_POST
def add_new_security_for_staff(request, secid):
    security = caches['default'].get('moex_secid_' + secid)
    if security:
        security.save()
        messages.success(request, 'Ценная бумага успешно добавлена.')
        return redirect(security.get_absolute_url())
    else:
        messages.error(request, 'Ценная бумага отсутствует в кэше.')
        return redirect(request.META.get('HTTP_REFERER'))


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
        elif re.search(r'ppif', description["TYPE"]):
            security_type = 'ppif'
        elif re.search(r'share', description["TYPE"]):
            security_type = 'share'
        elif re.search(r'futures', description["TYPE"]):
            security_type = 'futures'
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
                              newitem, timeout=24 * 60 * 60)
    else:
        newitem = caches['default'].get('moex_secid_' + description["SECID"])
    return newitem


@login_required
def new_security_detail(request, secid):
    newitem = prepare_new_security_by_secid(secid)
    # print(newitem.parce_url)
    return render(request,
                  'moex/detail.html',
                  {'security': newitem,
                   'security_in_user_portfolios': None,
                   'new_security': True})


def upload_moex_history(parce_url, secid, security_type, facevalue):
    security_history = moex_history(parce_url)
    if security_type == 'bond':
        for i in security_history:
            try:
                security_history[i]['CLOSE'] = str(
                    float(security_history[i]['CLOSE']) * float(facevalue)
                    / 100)
            except Exception:
                pass
                #security_history.pop(i)
    days = sorted(
        security_history,
        key=lambda i: datetime.strptime(i, '%d.%m.%Y').date(),
        reverse=True)
    result_history = {i: security_history[i]['CLOSE'] for i in days}
    caches['default'].add('moex_security_history_secid' + secid,
                          result_history, timeout=30)
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


@login_required
def security_sell(request, id):
    portfolio_id = request.GET.get('portfolio')
    security_id = id

    return render(request,
                  'security/list.html',
                  {'securities': securities})


def updated_portfolio(portfolio):
    return {'today_cash': str(portfolio.today_cash),
            'ostatok': str(portfolio.ostatok)}


@login_required
def delete_history(request, id):
    # переписать
    try:
        trade_history = TradeHistory.objects.get(id=id)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id_security_history'})
    if trade_history.owner != request.user:
        return JsonResponse({'status': 'not_owner'})
    status = trade_history.delete()
    content = {'status': status}
    if status == 'ok':
        content.update(updated_portfolio(trade_history.portfolio))
    # print(content)
    return JsonResponse(content)


@staff_only
def refresh_security(request, id):
    try:
        security = Security.objects.get(id=id)
        status, price, last_update = security.refresh_price(force=True)
        return JsonResponse({'status': status,
                             'price': price,
                             'last_update': last_update})
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id_security'})


@login_required
def sp(request, id_p, id_s):
    ostatok = 0
    ostatok_sec = 0
    try:
        portfolio = request.user.portfolios.get(id=id_p)
        ostatok = portfolio.ostatok
    except ObjectDoesNotExist:
        ostatok = 0
    try:
        security = Security.objects.get(id=id_s)
        s_p = portfolio.securities.get(
            security=security)
        ostatok_sec = s_p.count
    except ObjectDoesNotExist:
        ostatok_sec = 0
    ostatok = str(ostatok)
    return JsonResponse({'status': 'ok',
                         'ostatok_sec': ostatok_sec,
                         'ostatok': ostatok})


def get_security_history(request, id):
    try:
        security = Security.objects.get(id=id)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id_security'})
    date_since = request.GET.get('date_since') or None
    date_until = request.GET.get('date_until') or datetime.now().date()
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
    content = dict()
    content['history'] = result_history
    content['status'] = 'ok'
    content['url'] = reverse('moex:buy', args=[security.id])
    return JsonResponse(content)


def get_new_security_history(request, secid):
    if caches['default'].get('moex_secid_' + secid):
        newitem = caches['default'].get('moex_secid_' + secid)
    else:
        return JsonResponse({'status': 'no_secid_security'})
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
    content = dict()
    content['history'] = result_history
    content['status'] = 'ok'
    content['url'] = reverse('moex:new_buy', args=[secid])
    return JsonResponse(content)

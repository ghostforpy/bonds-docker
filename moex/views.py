from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.core.cache import caches
import threading
from .models import *
from .forms import *
from .iss_simple_main import search as moex_search,\
    specification as moex_specification,\
    history as moex_history
# Create your views here.


@cache_page(60 * 60)
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


def new_security_detail(request, secid):
    pass


@cache_page(24 * 60 * 60)
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
            if not caches['default'].get('moex_search_' + query):
                t = threading.Thread(
                    target=upload_search_moex_to_cache, args=(query,))
                t.start()
            else:
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
    cache = caches['default']
    result = cache.get('moex_search_' + query)
    content = {}
    if result:
        content['response'] = result
        content['status'] = 'ok'
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
        portfolios = request.user.portfolios.all()
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
    pass


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
        security = get_object_or_404(Security, id=id)
        status, price = security.refresh_price()
        return JsonResponse({'status': status, 'price': price})
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


@cache_page(60 * 15)
def get_security_history(request, id):
    try:
        security = get_object_or_404(Security, id=id)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id_security'})
    date_since = request.GET.get('date_since') or None
    date_until = request.GET.get('date_until') or datetime.now().date()
    cache = caches['default']
    security_history = cache.get('security_history_by_id' + str(security.id))
    if security_history is None:
        security_history = security.get_history(date_since,
                                                date_until,
                                                format_result='str')
    content = dict()
    content['history'] = security_history
    content['status'] = 'ok'
    content['url'] = reverse('moex:buy', args=[security.id])
    return JsonResponse(content)

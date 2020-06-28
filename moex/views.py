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
# Create your views here.


def upload(security):
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
        # блок кеширования вынесен в асинхрон
        t = threading.Thread(target=upload, args=(security,))
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


def security_list(request):
    form = SearchForm()
    query = None
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
                   'form': form,
                   'query': query})


def security_search_moex(request):
    q = request.GET.get('q')
    securities_list = Security.objects.filter(Q(name__icontains=q) |
                                              Q(code__icontains=q) |
                                              Q(fullname__icontains=q) |
                                              Q(regnumber__icontains=q) |
                                              Q(secid__icontains=q) |
                                              Q(isin__icontains=q) |
                                              Q(emitent__icontains=q)
                                              )
    return render(request,
                  'security/list.html',
                  {'securities': securities_list})


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
    #print(content)
    return JsonResponse(content)


@staff_only
def refresh_security(request, id):
    try:
        security = get_object_or_404(Security, id=id)
        status, price = security.refresh_price()
        return JsonResponse({'status': status, 'price': price})
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id_security'})


@ login_required
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

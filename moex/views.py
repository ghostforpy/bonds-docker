from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.db.models import Prefetch
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.core.cache import caches
import threading
from .models import *
from .forms import *
# from .iss_simple_main import history as moex_history
#    specification as moex_specification,\
from .utils import upload_history,\
    staff_only,\
    prepare_new_security_by_secid,\
    security_search_in_db,\
    security_search_in_moex,\
    get_new_security_history as get_new_sec_hist,\
    get_security_in_db_history_from_moex
# upload_search_moex_to_cache,\

# Create your views here.


@login_required
def security_detail(request, id):
    try:
        security = Security.objects.get(id=id)
        security_in_user_portfolios = None
        if request.user.is_authenticated:
            user = request.user
            security_in_user_portfolios = security.portfolios.filter(
                owner=user)
        # блок кеширования исторических данных поценной бумаге
        # для дальнейшей загрузки через ajax-запрос
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


def security_list(request):
    form = SearchForm()
    query = None
    moex_dict = None
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            securities_list = security_search_in_db(query)
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
    res = security_search_in_moex(query)
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
        try:
            security = get_object_or_404(Security, id=id)
        except ObjectDoesNotExist:
            JsonResponse({'status': 'no security id'})
        portfolio_id = request.GET.get('portfolio')
        date = request.GET.get('date') or now().date()
        buy = True if request.GET.get('buy') == 'true' else False
        portfolios = request.user.portfolios.filter(manual=False)
        if security.main_board_faceunit != 'SUR':
            # если валюта ценной бумаги отличная от нуля
            # предварительно подгружаем SecurityPortfolios
            qs = SecurityPortfolios.objects.filter(
                security__security_type__exact='currency'
            ).filter(
                security__name__istartswith=security.
                main_board_faceunit
            )
            portfolios = portfolios.prefetch_related(
                Prefetch('securities',
                         queryset=qs,
                         to_attr='sec')
            )
        portfolio = None
        for i in portfolios:
            if security.main_board_faceunit != 'SUR':
                # если валюта ценной бумаги отличная от нуля
                # на рендер страницы отправляем количество валюты
                # как остаток в портфеле
                if i.sec:
                    i.ostatok = i.sec[0].count
                else:
                    i.ostatok = 0
            if i.id == portfolio_id:
                portfolio = i
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
    security = caches['default'].get('moex_secid_' + secid)
    if not security:
        security = caches['default'].get('yfinance_secid_' + secid)
    if not security:
        return redirect(reverse('moex:list'))
    portfolios = request.user.portfolios.filter(manual=False)
    if security.main_board_faceunit != 'SUR':
        # если валюта ценной бумаги отличная от нуля
        # предварительно подгружаем SecurityPortfolios
        qs = SecurityPortfolios.objects.filter(
            security__security_type__exact='currency'
        ).filter(
            security__name__istartswith=security.
            main_board_faceunit
        )
        portfolios = portfolios.prefetch_related(
            Prefetch('securities',
                     queryset=qs,
                     to_attr='sec')
        )
    for i in portfolios:
        if security.main_board_faceunit != 'SUR':
            # если валюта ценной бумаги отличная от нуля
            # на рендер страницы отправляем количество валюты
            # как остаток в портфеле
            if i.sec:
                i.ostatok = i.sec[0].count
            else:
                i.ostatok = 0
    buy = True

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


@staff_only
@require_POST
def add_new_security_for_staff(request, secid):
    security = caches['default'].get('moex_secid_' + secid)
    if not security:
        security = caches['default'].get('yfinance_secid_' + secid)
    if security:
        security.save()
        messages.success(request, 'Ценная бумага успешно добавлена.')
        return redirect(security.get_absolute_url())
    else:
        messages.error(request, 'Ценная бумага отсутствует в кэше.')
        return redirect(request.META.get('HTTP_REFERER'))


@login_required
def new_security_detail(request, secid):
    newitem = prepare_new_security_by_secid(secid)
    if newitem:
        return render(request,
                      'moex/detail.html',
                      {'security': newitem,
                       'security_in_user_portfolios': None,
                       'new_security': True})
    else:
        messages.error(request, 'Ценная бумага не найдена')
        return redirect(request.META.get('HTTP_REFERER'))


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
        security = Security.objects.get(id=id_s)
        s_p = security.portfolios.get(
            portfolio__id=id_p)
        ostatok_sec = s_p.count
    except ObjectDoesNotExist:
        ostatok_sec = 0
    try:
        portfolio = request.user.portfolios.get(id=id_p)
        if security.main_board_faceunit != 'SUR':
            # если валюта ценной бумаги отличная от нуля
            # предварительно подгружаем SecurityPortfolios
            try:
                valute = portfolio.securities.filter(
                    security__name__istartswith=security.
                    main_board_faceunit
                ).get()
                ostatok = valute.count
            except ObjectDoesNotExist:
                ostatok = 0
        else:
            ostatok = portfolio.ostatok
    except ObjectDoesNotExist:
        ostatok = 0

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
    result_history = get_security_in_db_history_from_moex(security,
                                                          date_since,
                                                          date_until)
    content = dict()
    content['history'] = result_history
    content['status'] = 'ok'
    content['currency'] = security.get_main_board_faceunit_display()
    content['url'] = reverse('moex:buy', args=[security.id])
    return JsonResponse(content)


def get_new_security_history(request, secid):
    res = get_new_sec_hist(secid)
    if res['status'] == 'no_secid_security':
        return JsonResponse(res)
    result_history = res['result_history']
    content = dict()
    content['history'] = result_history
    content['status'] = 'ok'
    content['currency'] = res['currency']
    content['url'] = reverse('moex:new_buy', args=[secid])
    return JsonResponse(content)


@ require_POST
@ login_required
def security_follow(request, id):
    try:
        security = Security.objects.get(id=id)
        content = {'status': 'ok'}
        if request.user in security.users_follows.all():
            security.users_follows.remove(request.user)
            content['result'] = 'removed'
        else:
            security.users_follows.add(request.user)
            content['result'] = 'added'
        security.save()
        return JsonResponse(content)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id'})

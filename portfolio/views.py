from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .models import InvestmentPortfolio, PortfolioInvestHistory
from .forms import PortfolioCreateForm, PortfolioInvestForm, RefreshPortfolio
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import viewsets
from .serializers import InvestmentPortfolioSerializer
from moex.models import SecurityPortfolios, TradeHistory

# Create your views here.


def trigger_error(request):
    division_by_zero = 5 / 0


def updated_portfolio(portfolio):
    return {'today_cash': str(portfolio.today_cash),
            'invest_cash': str(portfolio.invest_cash),
            'percent_profit': str(portfolio.percent_profit),
            'year_percent_profit': str(portfolio.year_percent_profit),
            'ostatok': str(portfolio.ostatok)}


def portfolio_detail(request, id):
    try:
        qs_no_valute = SecurityPortfolios.objects.all().exclude(
            security__security_type='currency').prefetch_related('security')
        qs_valute = SecurityPortfolios.objects.all().filter(
            security__security_type='currency').prefetch_related('security')
        qs_trade = TradeHistory.objects.all().prefetch_related('security')
        qs_invests = PortfolioInvestHistory.objects.all()
        portfolio = InvestmentPortfolio.objects.prefetch_related(
            Prefetch('owner', to_attr='own'),
        ).get(id=id)

        history = None
        form_refresh = None
        owner_url = None
        owner_name = None
        #res = True
        securities_result = None
        portfolio_title = portfolio.title
        if portfolio.own == request.user:
            portfolio = InvestmentPortfolio.objects.prefetch_related(
                Prefetch('securities', queryset=qs_no_valute, to_attr='securit'),
                Prefetch('securities', queryset=qs_valute, to_attr='valute'),
                Prefetch('trade_securities', queryset=qs_trade, to_attr='trade'),
                Prefetch('portfolio_invests', queryset=qs_invests, to_attr='invests')
            ).get(id=id)
            history = portfolio.invests
            form_refresh = RefreshPortfolio(instance=portfolio)
            securities = portfolio.securit
            securities_result = set(i.security for i in securities)
            owner = True
        else:
            owner = False
            if portfolio.request_user_has_permission(request.user, check_owner=False):
                portfolio = InvestmentPortfolio.objects.prefetch_related(
                    Prefetch('securities', queryset=qs_no_valute, to_attr='securit'),
                ).get(id=id)
            else:
                owner_url = portfolio.own.get_absolute_url()
                owner_name = portfolio.own.name or portfolio.own.username
                portfolio = None
        return render(request,
                      'portfolio/detail.html',
                      {'portfolio': portfolio,
                       'owner': owner,
                       'securities_result': securities_result,
                       'form_refresh': form_refresh,
                       'history': history,
                       'owner_url': owner_url,
                       'owner_name': owner_name,
                       'portfolio_title': portfolio_title})
    except ObjectDoesNotExist:
        return redirect(request.META.get('HTTP_REFERER'))


@ require_POST
@ login_required
def portfolio_add_invest(request, id):
    form = PortfolioInvestForm(data=request.POST)
    print(request.POST)
    if form.is_valid():
        try:
            portfolio = InvestmentPortfolio.objects.get(id=id)
            if portfolio.owner == request.user:
                new_item = form.save(commit=False)
                new_item.portfolio = portfolio
                status = new_item.save()
                portfolio.refresh_portfolio()
                content = {'status': status}
                if status == 'ok':
                    content.update({'id': str(new_item.id)})
                    content.update(updated_portfolio(portfolio))
                    return JsonResponse(content)
                else:
                    return JsonResponse(content)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'no_id'})
    return JsonResponse({'status': 'no_valid'})


@ require_POST
@ login_required
def refresh_portfolio(request, id):
    form = RefreshPortfolio(data=request.POST)
    if form.is_valid():
        try:
            portfolio = InvestmentPortfolio.objects.get(id=id)
            if portfolio.owner == request.user:
                portfolio.today_cash = form.cleaned_data['today_cash']
                portfolio.private = form.cleaned_data['private']
                portfolio.refresh_portfolio()
                content = {'status': 'ok'}
                content.update(updated_portfolio(portfolio))
                return JsonResponse(content)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'no_id'})
    return JsonResponse({'status': 'no_valid'})


@ require_POST
@ login_required
def portfolio_del_invest(request, id):
    try:
        invest = PortfolioInvestHistory.objects.get(id=id)
        if invest.portfolio.owner == request.user:
            portfolio = invest.portfolio
            status = invest.delete()
            content = {'status': status}
            if status == 'ok':
                content.update(updated_portfolio(portfolio))
            return JsonResponse(content)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id'})


def portfolio_list(request):
    portfolios = InvestmentPortfolio.objects.select_related('owner').all()

    return render(request,
                  'portfolio/list.html',
                  {'portfolios': portfolios})


@ login_required
def my_portfolios(request):
    my_portfolios = request.user.portfolios.all()
    return render(request,
                  'portfolio/my_list.html',
                  {'portfolios': my_portfolios})


@ login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioCreateForm(data=request.POST)
        if form.is_valid():
            try:
                # find already added same title portfolio by same title and user
                i = InvestmentPortfolio.objects.get(owner=request.user,
                                                    title=form.
                                                    cleaned_data['title'])
                messages.error(
                    request, 'Портфель с таким названием вами уже добавлен '
                    + str(i.created))
                return redirect(i.get_absolute_url())
            except ObjectDoesNotExist:
                # there are not same images
                pass
            new_item = form.save(commit=False)
            # add user to new item
            new_item.owner = request.user
            new_item.save()
            messages.success(request, 'Портфель успешно создан.')
            return redirect(new_item.get_absolute_url())
        messages.error(request, 'Не валид')
        return render(request, 'portfolio/create.html',
                      {'form': form})
    else:
        # request is GET
        form = PortfolioCreateForm(data=request.GET)
        return render(request, 'portfolio/create.html',
                      {'form': form})


@ login_required
def delete_portfolio(request, id):
    try:
        portfolio = InvestmentPortfolio.objects.get(
            owner=request.user, id=id
        )
    except ObjectDoesNotExist:
        return redirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST':
        if portfolio.today_cash == 0 and portfolio.ostatok == 0:
            messages.success(request, 'Портфель {} успешно удалён.'
                             .format(portfolio.title))
            portfolio.delete()
            return redirect(reverse('portfolio:my_portfolios'))
        else:
            messages.error(
                request, 'Остаток и текущий баланс должны быть равны 0.')
            return redirect(portfolio.get_absolute_url())
    else:
        return render(request, 'portfolio/delete.html',
                      {'portfolio': portfolio})


class InvestmentPortfolioViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = InvestmentPortfolio.objects.all()
    serializer_class = InvestmentPortfolioSerializer
    http_method_names = ['get', 'head']


@ require_POST
@ login_required
def portfolio_follow(request, id):
    try:
        portfolio = InvestmentPortfolio.objects.get(id=id)
        content = {'status': 'ok'}
        if request.user in portfolio.users_follows.all():
            portfolio.users_follows.remove(request.user)
            content['result'] = 'removed'
        else:
            portfolio.users_follows.add(request.user)
            content['result'] = 'added'
        portfolio.save()
        return JsonResponse(content)
    except ObjectDoesNotExist:
        return JsonResponse({'status': 'no_id'})

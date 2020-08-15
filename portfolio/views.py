from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InvestmentPortfolio, PortfolioInvestHistory
from .forms import PortfolioCreateForm, PortfolioInvestForm, RefreshPortfolio
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import viewsets
from .serializers import InvestmentPortfolioSerializer

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
        portfolio = InvestmentPortfolio.objects.get(id=id)
        history = None
        form_refresh = None
        owner_url = portfolio.owner.get_absolute_url()
        owner_name = portfolio.owner.name or portfolio.owner.username
        portfolio_title = portfolio.title
        res = True
        securities_result = None
        if portfolio.owner == request.user:
            history = portfolio.portfolio_invests.all()
            form_refresh = RefreshPortfolio(instance=portfolio)
            securities = portfolio.trade_securities.all()
            securities_result = set(i.security for i in securities)
            res = False
        if res and (portfolio.private == 'da'):
            portfolio = None
            res = False
        if res and (portfolio.private == 'aa'):
            res = False
        if res and (not(request.user.is_authenticated) and
                    (portfolio.private == 'al')):
            portfolio = None
            res = False
        if res and (request.user.is_authenticated and
                    (portfolio.private == 'af')):
            if not request.user.friends.is_friend(portfolio.owner.friends):
                portfolio = None
            res = False
        return render(request,
                      'portfolio/detail.html',
                      {'portfolio': portfolio,
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
            portfolio = get_object_or_404(InvestmentPortfolio,
                                          id=id)
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
            portfolio = get_object_or_404(InvestmentPortfolio,
                                          id=id)
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
    portfolios = InvestmentPortfolio.objects.all()

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
        portfolio = get_object_or_404(InvestmentPortfolio, id=id)
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

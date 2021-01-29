from decimal import Decimal
from django.core.cache import caches
from rest_framework.serializers import ValidationError
from portfolio.models import PortfolioInvestHistory
from moex.utils import get_or_prepare_new_security_by_secid
from moex.utils_valute import get_valute_curse
from moex.models import Security, TradeHistory, SecurityPortfolios


cache = caches['default']


def get_security(br, securities_in_db, isin):
    try:
        if not cache.get('security_{}'.format(isin)):
            sec = list(filter(lambda x: x.isin == isin, securities_in_db))
            if sec:
                if len(sec) > 1:
                    raise Exception('multiple securities')
                sec = sec[0]
            else:
                sec = br.get_security_by_secid_isin(isin=isin)
                sec = get_or_prepare_new_security_by_secid(sec.secid)
                sec.save()
            cache.add('security_{}'.format(isin),
                      sec, timeout=60 * 60)
        else:
            sec = cache.get('security_{}'.format(isin))
    except Exception as e:
        # print(e)
        sec = None
    return sec


def create_portfolio_by_broker_report(portfolio, br):
    # проверка нулевых входящих остатков
    if not br.check_zero_incoming_balance_money() or\
            not br.check_zero_incoming_balance_securities():
        raise ValidationError("incoming balance must be zero")

    securities = list(
        map(lambda x: x.isin, br.securities_info),
    )
    securities_in_db = Security.objects.filter(isin__in=securities)
    # добавить валюты к queryset
    securities_in_db = securities_in_db.union(
        Security.objects.filter(security_type='currency')
    )
    # секция добавления операций получения доходов
    profit_operations = br.return_all_profit_operations()
    profit_operations_list = list()
    for i in profit_operations:
        item = PortfolioInvestHistory(
            action='tp',
            date=i.date,
            portfolio=portfolio,
            cash=i.cash,
            ndfl=i.tax,
            currency=i.currency.replace('RUB', 'SUR'),
            security=get_security(br, securities_in_db, i.isin)
        )
        profit_operations_list.append(item)

    # секция добавления операций broker_taxes
    broker_taxes = br.return_list_broker_taxes()
    broker_taxes_list = list()
    for i in broker_taxes:
        item = PortfolioInvestHistory(
            action='bc',
            date=i.execution_date,
            portfolio=portfolio,
            cash=i.withdrawal_amount,
            currency=i.currency.replace('RUB', 'SUR')
        )
        broker_taxes_list.append(item)

    # секция добавления операций amortisations
    amortisations = br.return_list_amortisations()
    # подсекция добавления операций частичного погашения
    part_amortisations = list(
        filter(lambda x: not x.full, amortisations)
    )
    part_amortisations_list = list()
    for i in part_amortisations:
        item = PortfolioInvestHistory(
            action='br',
            date=i.date,
            portfolio=portfolio,
            cash=i.cash,
            currency=i.currency.replace('RUB', 'SUR'),
            security=get_security(br, securities_in_db, i.isin)
        )
        part_amortisations_list.append(item)
    # подсекция добавления операций полного погашения
    # как операции продажи по номинальной цене облигации
    full_amortisations = list(
        filter(lambda x: x.full, amortisations)
    )
    full_amortisations_list = list()
    for i in full_amortisations:
        item = TradeHistory(
            owner=portfolio.owner,
            portfolio=portfolio,
            security=get_security(br, securities_in_db, i.isin),
            date=i.date,
            buy=False,
            count=i.count,
            price=Decimal(i.cash / i.count))
        full_amortisations_list.append(item)

    # секция добавления операций ввода/вывода денег
    invest_operations = br.return_all_invests_operations()
    invest_operations_list = list()
    for i in invest_operations:
        item = PortfolioInvestHistory(
            action='vp' if i.action else 'pv',
            date=i.date,
            portfolio=portfolio,
            cash=i.cash,
            cash_in_rub=i.cash,
            currency=i.currency.replace('RUB', 'SUR')
        )
        if i.currency not in ['SUR', 'RUB']:
            item.cash_in_rub = item.cash * Decimal(get_valute_curse(
                item.currency, date=item.date
            ))
        invest_operations_list.append(item)

    # секция добавления операций покупок/продаж ценных бумаг
    transactions = br.transactions
    transactions_list = list()
    for i in transactions:
        item = TradeHistory(
            owner=portfolio.owner,
            portfolio=portfolio,
            security=get_security(br, securities_in_db, i.isin),
            date=i.date,
            buy=i.action == 'Покупка',
            price=i.price,
            commission=i.broker_commission,
            count=i.count,
            nkd=i.nkd
        )
        transactions_list.append(item)
    # запись в базу
    PortfolioInvestHistory.objects.bulk_create(
        profit_operations_list +
        broker_taxes_list +
        part_amortisations_list +
        invest_operations_list
    )
    TradeHistory.objects.bulk_create(
        full_amortisations_list + transactions_list
    )

    # секция обновления остатка рублей в портфеле
    money_movement = br.money_movement
    portfolio.ostatok = money_movement['RUB'].plan_outgoing_balance

    # секция обновления остатка валюты в портфеле
    security_in_portfolio_list = list()
    for i in money_movement:
        if i == 'RUB':
            continue
        if money_movement[i].plan_outgoing_balance == Decimal(0):
            continue
        valute = get_security(br, securities_in_db, i)
        new_item = SecurityPortfolios(
            owner=portfolio.owner,
            portfolio=portfolio,
            security=valute,
            count=money_movement[i].plan_outgoing_balance,
            today_price=valute.today_price,
            total_cost=money_movement[i].plan_outgoing_balance *
            valute.today_price,
            total_cost_in_rub=money_movement[i].plan_outgoing_balance *
            valute.today_price
        )
        security_in_portfolio_list.append(new_item)

    # секция обновления остатка ценных бумаг в портфеле
    securities_movement = br.securities_movement
    for i in securities_movement:
        if i.outgoing_balance == Decimal(0):
            continue
        security = get_security(br, securities_in_db, i.isin)
        new_item = SecurityPortfolios(
            owner=portfolio.owner,
            portfolio=portfolio,
            security=security,
            count=i.outgoing_balance,
            today_price=security.today_price,
            total_cost=i.outgoing_balance * security.today_price,
            total_cost_in_rub=i.outgoing_balance * security.today_price
        )
        if security.main_board_faceunit != 'SUR':
            valute = get_security(
                br, securities_in_db, security.main_board_faceunit
            )
            new_item.total_cost_in_rub = new_item.total_cost *\
                valute.today_price
        security_in_portfolio_list.append(new_item)
    # запись в базу
    SecurityPortfolios.objects.bulk_create(
        security_in_portfolio_list
    )
    # обновление портфеля
    portfolio.refresh_portfolio()

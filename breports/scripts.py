from decimal import Decimal
from rest_framework.serializers import ValidationError
from .broker_parser.classes import BrokerReport, FileNotSupported
from .broker_parser.parsers import AVAILEBLE_PARSERS, TinkoffParserXLS
from portfolio.scripts import year_profit_approx
from moex.iss_simple_client import NoSecuritySecid
from moex.iss_simple_main import get_security_by_secid_isin
from moex.utils import (get_new_security_history_from_moex,
                        prepare_new_security_by_secid,
                        get_today_price_by_secid,
                        get_security_by_secid,
                        get_valute_curse)
from .api.serializers import (InvestsOperationSerializer,
                              NonZeroSecuritySerializer)
import xlrd


def check_supported_file(f):
    # only xls/xlsx file is supported
    try:
        xlrd.open_workbook(filename=f)
    except xlrd.biffh.XLRDError:
        raise FileNotSupported


def init_broker_report(filename, parser=TinkoffParserXLS):
    check_supported_file(filename)
    return BrokerReport(parser, filename)


def return_invest_operations(broker_report):
    pass


def rr(broker_report):
    return broker_report.return_invests_operations_list_by_currency()


class CountSecurity():
    def __init__(self, count, security):
        self.count = count
        try:
            self.security = get_security_by_secid(security.secid)
        except NoSecuritySecid:
            raise ValidationError("can't find security.secid")
        self.total = self.count * Decimal(self.security.today_price)
        if self.security.faceunit != 'SUR':
            curse = get_valute_curse(self.security.faceunit)
            self.price_in_rub = float(self.security.today_price) * curse
            self.total_in_rub = self.price_in_rub * self.count
        else:
            self.price_in_rub = 0
            self.total_in_rub = 0


def return_non_zero_securities(broker_report):
    temp = broker_report.return_none_zero_securities()
    result = list()
    for i in temp:
        result.append(CountSecurity(*i))
    return result


def calc_year_profit(broker_report):
    # пока что только по RUB
    # проверка нулевых входящих остатков
    if not broker_report.check_zero_incoming_balance_money() or\
            not broker_report.check_zero_incoming_balance_securities():
        raise ValidationError("incoming balance must be zero")
    currencies = broker_report.return_currency_money_movements()
    invests = list()
    for i in currencies:
        temp = broker_report.\
            return_invests_operations_list_by_currency(i)
        if i != 'RUB':
            temp = map(lambda x: [
                x[0] * Decimal(get_valute_curse(i, x[1])),
                x[1]],
                temp)
        invests += temp
    securities = broker_report.\
        return_non_zero_outgoing_balance_securities()
    today_cash = Decimal(0)
    for i in securities:
        try:
            today_price = Decimal(get_today_price_by_secid(i.secid))
        except NoSecuritySecid:
            raise ValidationError("can't find i.secid")
        today_cash += today_price * i.outgoing_balance

    for cur in currencies:
        try:
            outgoing_balance = broker_report.money_movement[cur]\
                .outgoing_balance
            if cur != 'RUB':
                outgoing_balance *= Decimal(get_valute_curse(cur))
            today_cash += outgoing_balance
        except KeyError:
            continue
    year_profit = year_profit_approx(invests, today_cash)
    invests = broker_report.return_all_invests_operations()
    for i in invests:
        if i.currency == 'RUB':
            i.cash_in_rub = i.cash
        else:
            i.cash_in_rub = i.cash * Decimal(get_valute_curse(
                i.currency,
                i.date))
    invests = InvestsOperationSerializer(
        sorted(broker_report.return_all_invests_operations(),
               key=lambda x: x.date),
        many=True
    ).data
    non_zero_securities = NonZeroSecuritySerializer(
        return_non_zero_securities(broker_report),
        many=True
    ).data
    result = {
        'year_profit': year_profit,
        'today_cash': today_cash,
        'invests': invests,
        'securities': non_zero_securities
    }
    return result

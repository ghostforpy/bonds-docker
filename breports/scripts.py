from decimal import Decimal
from rest_framework.serializers import ValidationError
from .broker_parser.classes import (BrokerReport,
                                    FileNotSupported,
                                    NeedEarlierBrokerReport)
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
                              NonZeroSecuritySerializer,
                              IncomeCertificateSecuritySerializer,
                              ProfitSerializer,
                              ProfitSellSerializer)
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
            raise ValidationError("can't find {}".format(security.secid))
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


class IncomeCertificateSecurity():
    def __init__(self, security, count, participation_basis):
        try:
            self.security = get_security_by_secid(security.secid)
        except NoSecuritySecid:
            raise ValidationError("can't find {}".format(security.secid))
        self.count = count
        self.participation_basis = participation_basis


class Profit():
    def __init__(self, value, currency):
        self.value = value
        self.currency = currency


class ProfitSell():
    def __init__(self,
                 secid,
                 total_profit,
                 total_tax_base_without_commissions,
                 total_commissions,
                 total_tax_base):
        try:
            self.security = get_security_by_secid(secid)
        except NoSecuritySecid:
            raise ValidationError("can't find {}".format(security.secid))
        self.total_profit = total_profit
        self.total_tax_base_without_commissions = total_tax_base_without_commissions
        self.total_commissions = total_commissions
        self.total_tax_base = total_tax_base


def income_certificate(broker_report):
    securities = broker_report.\
        return_none_zero_securities()
    # проверка нулевых входящих остатков бумаг,
    # по которым исходящий остаток больше 0.
    securities_movements = broker_report.\
        return_non_zero_outgoing_balance_securities()
    for i in securities_movements:
        if i.incoming_balance > Decimal(0):
            raise ValidationError(
                "incoming balance security must be zero ({})".format(i[1].secid))
    part_five_one_temp = list()
    part_five_two_temp = list()
    for i in securities_movements:
        security = broker_report.get_security_by_secid_isin(i.secid)
        t = IncomeCertificateSecurity(
            i,
            i.outgoing_balance,
            []
        )
        if t.security.security_type == 'share':  # проверка типа бумаги
            try:
                participation_basis = broker_report.return_docum_by_secid_isin(
                    i.secid, raise_exceptions=True
                )
            except NeedEarlierBrokerReport:
                raise ValidationError(
                    "Need Earlier Broker Report by ({})".format(i.secid))
            t.participation_basis = sorted(participation_basis,
                                           key=lambda x: x.date)
            part_five_one_temp.append(t)
        else:
            part_five_two_temp.append(t)
    participation_basis_share = IncomeCertificateSecuritySerializer(
        part_five_one_temp,
        many=True
    ).data
    participation_basis_other = IncomeCertificateSecuritySerializer(
        part_five_two_temp,
        many=True
    ).data

    profit_sells = list()
    securities_sells = [
        i for i in broker_report.securities_movement if i.writeoff > Decimal(0)
    ]
    for i in securities_sells:
        try:
            profit_and_taxes = broker_report.\
                return_profit_and_taxes_sell_bonds_by_secid_isin(
                    i.secid,
                    raise_exceptions=True
                )
            if profit_and_taxes['total_profit'] > Decimal(0):
                profit_sells.append(
                    ProfitSell(i.secid, **profit_and_taxes)
                )
        except:
            continue
    profits = dict()
    if profit_sells:
        profits['sells'] = ProfitSellSerializer(
            profit_sells,
            many=True
        ).data
    profit_div_coupon = broker_report.total_profit()
    profit_repo = broker_report.total_profit_repo()
    if profit_div_coupon:
        profits['profit_div_coupon'] = ProfitSerializer(
            [Profit(profit_div_coupon[i], i) for i in profit_div_coupon],
            many=True
        ).data
    if profit_repo:
        profits['profit_repo'] = ProfitSerializer(
            [Profit(profit_div_coupon[i], i) for i in profit_repo],
            many=True
        ).data
    result = {
        'profits': profits,
        'part_five_one': participation_basis_share,
        'part_five_two': participation_basis_other
    }
    return result

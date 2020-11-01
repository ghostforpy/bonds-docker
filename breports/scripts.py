from decimal import Decimal
from rest_framework.serializers import ValidationError
from .broker_parser.classes import BrokerReport, FileNotSupported
from .broker_parser.parsers import AVAILEBLE_PARSERS, TinkoffParserXLS
from portfolio.scripts import year_profit_approx
from moex.iss_simple_main import get_security_by_secid_isin
from moex.utils import (get_new_security_history_from_moex,
                        prepare_new_security_by_secid,
                        get_today_price_by_secid)
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
        self.security = security


def return_non_zero_securities(broker_report):
    temp = broker_report.return_none_zero_securities()
    result = list()
    for i in temp:
        result.append(CountSecurity(*i))
    return result


def calc_year_profit(broker_report):
    # пока что только по RUB
    # проверка нулевых входящих остатков
    if not broker_report.check_zero_incoming_balance_money or\
            not broker_report.check_zero_incoming_balance_securities:
        raise ValidationError("incoming balance must be zero")
    invests = broker_report.\
        return_invests_operations_list_by_currency()
    securities = broker_report.\
        return_non_zero_outgoing_balance_securities()
    today_cach = Decimal(0)
    for i in securities:
        today_price = Decimal(get_today_price_by_secid(i.secid))
        today_cach += today_price * i.outgoing_balance
    today_cach += broker_report.money_movement['RUB'].outgoing_balance
    result = year_profit_approx(invests, today_cach)
    return result

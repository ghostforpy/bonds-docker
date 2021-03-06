from django import template
# from ..models import *
# from bonds.friends.models import UserFriends
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='user_has_security')
def user_has_security(user, security):
    security_portfolios = security.portfolios.filter(owner=user)
    return security_portfolios.count()


@register.filter(name='count_security_in_portfolio')
def count_security_in_portfolio(portfolio, security):
    try:
        security_portfolios = portfolio.securities.get(
            security=security)
    except ObjectDoesNotExist:
        return 0
    print(security_portfolios.id)
    return security_portfolios.count


@register.filter(name='user_trades_security')
def user_trades_security(user, security):
    security_trades = security.trades.filter(owner=user)
    return security_trades


@register.filter(name='int_to_str')
def int_to_str(s):
    if type(s) is str:
        s = float("{0:.7s}".format(s))
    else:
        s = float("{0:.7f}".format(s))
    return str(s)


@register.filter(name='delete_zeroes')
def delete_zeroes(s):
    if type(s) is str:
        s = float("{0:.2s}".format(s))
    else:
        s = float("{0:.2f}".format(s))
    return s


@register.filter(name='return_color_and_fas_bootstrap')
def return_color(i, fas=False):
    i = float(i)
    if i < 0:
        result = 'text-danger'
        if fas:
            result += ' fas fa-angle-double-down'
        return result
    elif i > 0:
        result = 'text-success'
        if fas:
            result += ' fas fa-angle-double-up'
        return result
    else:
        return 'text-secondary'

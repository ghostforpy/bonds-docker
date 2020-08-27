from django import template
# from ..models import *
# from bonds.friends.models import UserFriends
# from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.filter(name='return_color')
def return_color(i):
    i = float(i)
    if i < 0:
        return 'red'
    elif i > 0:
        return 'green'
    else:
        return 'gray'


@register.filter(name='return_number_with_sign')
def return_number_with_sign(num):

    return "{0:+.2f}".format(float(num))


@register.filter(name='delete_zeroes')
def delete_zeroes(s):
    return float("{0:.2f}".format(s))

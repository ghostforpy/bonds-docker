from django.urls import re_path, path

from .tg_url_views import *

urlpatterns = [
    re_path(r'^securities_detail_(?P<id>[0-9]+)(_)*$', get_security_detail),
    re_path(r'^securities_new_(?P<isin>[A-Za-z0-9]*)(_)*$', get_new_security_detail),
    re_path(r'^security_(?P<id>[0-9]+)_history(_)*$', get_security_history),
    re_path(r'^security_new_(?P<isin>[A-Za-z0-9]*)_history(_)*$', get_new_security_history),
]

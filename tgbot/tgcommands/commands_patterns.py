from django.urls import re_path

from .commands_views import *


urlpatterns = [
    re_path('^start$', start),
    re_path('^help$', help),
    re_path('^config$', config),
    re_path('^getmode$', getmode),
    re_path('^search$', search)
]

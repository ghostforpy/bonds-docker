from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views_auth
app_name = 'tgbot'

urlpatterns = [
    path("telegram/login/", views_auth.telegram_login, name="telegram_login"),
]

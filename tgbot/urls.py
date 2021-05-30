from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import HandlerBotView
from .auth import views_auth

app_name = 'tgbot'

urlpatterns = [
    path("telegram/login/", views_auth.telegram_login, name="telegram_login"),
    path('', csrf_exempt(HandlerBotView.as_view()), name='handler'),
]

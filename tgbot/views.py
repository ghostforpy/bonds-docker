#from django.shortcuts import render
import os
import re
import requests

from django.http import JsonResponse
from django.views import View
from django.urls import resolve, Resolver404, reverse
from django.template.loader import render_to_string

from .classes import Message, CallbackQuery
from .types_classes import InlineKeyboard, InlineKeyboardButton
from .message_views import main_message_handle
from .callback_views import main_callback_handle


TELEGRAM_URL = "https://api.telegram.org/bot"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "error_token")


class HandlerBotView(View):
    login_required = True
    no_command_message = 'Команда не распознана'
    need_auth_message = render_to_string('tgbot/need_auth.html')

    def post(self, request, *args, **kwargs):
        def handle():
            temp = request.tg_body
            if isinstance(temp, Message):
                if re.match(r'^/[A-Za-z0-9]+(_[A-Za-z0-9]*)+', temp.text):
                    # '/url_url'
                    self._tg_url_handle(request)
                elif re.match(r'^/[A-Za-z]*$', temp.text):
                    # '/command'
                    self._command_handle(request)
                else:
                    self._message_handle(request)
            elif isinstance(temp, CallbackQuery):
                self._callback_query_handle(request)
        try:
            handle()
        except:
            pass
        finally:
            return JsonResponse({"ok": "POST request processed"})

    def is_login_required(self, request):
        if self.login_required and not request.user.is_authenticated:
            self.send_need_auth()
            return False
        return True

    @staticmethod
    def send_message(message, chat_id, reply_markup=None):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Html",
            "reply_markup": reply_markup
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", data=data
        )
        # print(response.text)

    @staticmethod
    def edit_message_text(message, chat_id, message_id, reply_markup=None):
        data = {
            "chat_id": chat_id,
            "text": message,
            "message_id": message_id,
            "parse_mode": "Html",
            "reply_markup": reply_markup
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/editMessageText", data=data
        )
        # print(response.text)

    @staticmethod
    def answer_callback_query(message, callback_query_id,
                              show_alert=True, url=None, cache_time=0):
        data = {
            "callback_query_id": callback_query_id,
            "text": message,
            "show_alert": show_alert,
            "cache_time": cache_time,
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/answerCallbackQuery", data=data
        )
        # print(response.text)

    def send_need_auth(self):
        login_url = self.request.build_absolute_uri(reverse('signup'))
        socialaccount_connections_url = self.request.build_absolute_uri(
            reverse('socialaccount_connections'))
        self.send_message(
            self.need_auth_message,
            self.request.tg_body.chat.id,
            reply_markup=InlineKeyboard(
                [
                    [InlineKeyboardButton('Для новых пользователей',
                                          url=login_url)],
                    [InlineKeyboardButton('Для зарегистрированных пользователей',
                                          url=socialaccount_connections_url)]
                ]
            ).to_json()
        )

    def _message_handle(self, request):
        if self.is_login_required(request):
            return main_message_handle(request, self)

    def _command_handle(self, request):
        try:
            func, args, kwargs = resolve(
                request.tg_body.text, 'tgbot.commands_patterns'
            )
        except Resolver404:
            return self.send_message(
                self.no_command_message, request.tg_body.chat.id
            )
        # check is login required
        if self.is_login_required(request):
            return func(request, self)

    def _tg_url_handle(self, request):
        try:
            func, args, kwargs = resolve(
                request.tg_body.text, 'tgbot.tg_url_patterns'
            )
        except Resolver404:
            return self.send_message(
                self.no_command_message, request.tg_body.chat.id
            )
        # check is login required
        if self.is_login_required(request):
            return func(request, self, **kwargs)

    def _callback_query_handle(self, request):
        return main_callback_handle(request, self)

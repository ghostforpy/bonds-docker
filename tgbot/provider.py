from allauth.socialaccount.providers.base import Provider, ProviderAccount
from allauth.socialaccount.adapter import get_adapter


class TelegramAccount(ProviderAccount):
    pass


class TelegramProvider(Provider):
    id = "telegram"
    name = "Telegram"
    account_class = TelegramAccount

    def get_login_url(self, request, **kwargs):
        # TODO: Find a way to better wrap the iframed button
        return "#"

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        ret = {}
        if data.get("first_name"):
            ret["username"] = data.get("first_name")
        if data.get("last_name"):
            ret["last_name"] = data.get("last_name")
        if data.get("username"):
            ret["username"] = data.get("username")
        return ret


provider_classes = [TelegramProvider]

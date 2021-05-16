import os
from sys import argv
import requests
from django.urls import reverse

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", False)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", False)
print('Set telegram webhook url')
if TELEGRAM_BOT_TOKEN and WEBHOOK_URL:

    url = 'https://api.telegram.org/bot{}/setWebhook?url={}/tgwebhook/'.format(
        TELEGRAM_BOT_TOKEN,
        WEBHOOK_URL
    )
    r = requests.post(url)
    json_response = r.json()
    print(json_response)
else:
    print('TELEGRAM_BOT_TOKEN=', TELEGRAM_BOT_TOKEN)
    print('WEBHOOK_URL=', WEBHOOK_URL)
exit()

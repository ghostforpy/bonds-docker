import os
import json
#from sys import argv
import requests

#from django.urls import reverse
from tgcommands import available_commands
#import sys


AVAILABLE_COMMANDS = available_commands.AVAILABLE_COMMANDS
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", False)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", False)

if TELEGRAM_BOT_TOKEN and WEBHOOK_URL:
    print('Set telegram webhook url')

    url = 'https://api.telegram.org/bot{}/setWebhook?url={}/tgwebhook/'.format(
        TELEGRAM_BOT_TOKEN,
        WEBHOOK_URL
    )
    r = requests.post(url)
    json_response = r.json()
    print(json_response)

    print('Set telegram bot commands')
    url = 'https://api.telegram.org/bot{}/setMyCommands'.format(
        TELEGRAM_BOT_TOKEN
    )
    commands = json.dumps([
        {'command': i, 'description': AVAILABLE_COMMANDS[i]} for i in AVAILABLE_COMMANDS
    ])
    r = requests.post(url, data={'commands': commands})
    json_response = r.json()
    print(json_response)
else:
    print('TELEGRAM_BOT_TOKEN=', TELEGRAM_BOT_TOKEN)
    print('WEBHOOK_URL=', WEBHOOK_URL)
exit()

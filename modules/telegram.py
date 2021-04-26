import os
import random
import time

import requests


class Telegram:
    def __init__(self, bot_token: str, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def write(self, text, tag):
        if os.environ.get('DEBUG') == 'True':
            tag = 'debug-all'
        data = {
            'chat_id': self.chat_id[tag],
            'text': text,
        }
        url = 'https://api.telegram.org/bot' + self.bot_token + '/'
        error_time = None
        last_time = 0
        while True:
            if time.time() - last_time >= random.randint(2, 10):
                last_time = time.time()
                if not requests.post(url + 'sendMessage', data=data).json()['ok']:
                    if error_time is None:
                        error_time = time.time()
                    elif last_time - error_time >= 3600:
                        raise ConnectionError('Ошибка отправки в Телеграм')
                else:
                    break

import os
import random
import time

import requests


class Telegram:
    def __init__(self, bot_token: str, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def write(self, text, tag='debug-all'):
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
            if time.time() - last_time >= random.randint(2, 5):
                last_time = time.time()
                answer = requests.post(url + 'sendMessage', data=data).json()
                if not answer['ok']:
                    if error_time is None:
                        error_time = time.time()
                    elif last_time - error_time >= 60:
                        raise ConnectionError('Telegram [' + str(answer['error_code']) + ']\n' + answer['description'])
                else:
                    break

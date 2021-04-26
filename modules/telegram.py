import os

import requests


class Telegram:
    def __init__(self, bot_token: str, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def write(self, text, tag):
        #  TODO: Цикл отправки чтоб не падало
        if os.environ.get('DEBUG') == 'True':
            tag = 'debug-all'
        data = {
            'chat_id': self.chat_id[tag],
            'text': text,
        }
        url = 'https://api.telegram.org/bot' + self.bot_token + '/'
        if not requests.post(url + 'sendMessage', data=data).json()['ok']:
            raise ConnectionError('Ошибка отправки в Телеграм')

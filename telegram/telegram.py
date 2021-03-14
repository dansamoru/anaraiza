from settings import *
import os
import requests


def write():
    with open(INPUT_FILE_PATH, 'r') as input_file:
        text = input_file.read()
        data = {
            'chat_id': CHAT_ID,
            'text': text,
        }
        url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/'
        print(requests.post(url + 'sendMessage', data=data).text)
    with open(INPUT_FILE_PATH, 'wb') as input_file:
        pass


def check() -> bool:
    return os.path.getsize(INPUT_FILE_PATH) > 0


if __name__ == '__main__':
    if check():
        write()

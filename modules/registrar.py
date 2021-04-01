import json
import os

import requests
from bs4 import BeautifulSoup


class Registrar:
    def __init__(self, config):
        self.api_url = config['api_url']
        self.__token__ = None
        self.__user__ = None
        with open('registrar.txt', 'w'):
            pass

    def __post_request__(self, url, data=None) -> requests.Response:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.111 YaBrowser/21.2.1.94 (beta) Yowser/2.5 Safari/537.36',
        }
        response = requests.post(self.api_url + url, headers=headers, data=data)
        return response

    def __get_request__(self, url, data=None) -> requests.Response:
        if self.__token__ is None:
            self.__authorize__()
        headers = {
            'authorization': 'bearer ' + self.__token__,
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.111 YaBrowser/21.2.1.94 (beta) Yowser/2.5 Safari/537.36',
        }
        response = requests.get(self.api_url + url, headers=headers, data=data)
        if response.status_code == 401:
            self.__authorize__()
            return self.__get_request__(url, data)
        return response

    def __authorize__(self):
        response = self.__post_request__('users/login/',
                                         {'user': os.getenv('REMANGS_USERNAME'),
                                          'password': os.getenv('REMANGA_PASSWORD')}).json()
        self.__token__ = response['content']['access_token']
        self.__user__ = response['content']

    def __get_csrf__(self):
        if self.__user__ is None:
            self.__authorize__()
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.111 YaBrowser/21.2.1.94 (beta) Yowser/2.5 Safari/537.36',
            'cookie': 'user=' + str(self.__user__).replace('\'', '\"').replace(' ', '').replace('False',
                                                                                                'false').replace('True',
                                                                                                                 'true').replace(
                'None', 'null'),
        }
        response: requests.Response = requests.get('https://remanga.org/panel/add-titles/', headers=headers)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', attrs={'name': 'csrfmiddlewaretoken'})['value']
            return csrf_token
        else:
            raise ValueError('Ошибка подключения к remanga')

    def __add_title__(self, data) -> bool:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.111 YaBrowser/21.2.1.94 (beta) Yowser/2.5 Safari/537.36',
            'cookie': 'user=' + str(self.__user__).replace('\'', '\"').replace(' ', '').replace('False',
                                                                                                'false').replace('True',
                                                                                                                 'true').replace(
                'None', 'null'),
        }
        if os.getenv('DEBUG') is False:
            response = requests.post('https://remanga.org/panel/add-titles/', headers=headers, data=data)
            return response.ok
        else:
            with open('registrar.txt', 'a') as file:
                file.write(str(data) + '\n')

    def __translate_name__(self, ko_name: str, lang: str):
        ko_name.replace('(연재)', '').replace('(연재)', '').replace('[만화]', '')
        url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Api-Key ' + os.getenv('TRANSLATOR_API_KEY'),
        }
        payload = {
            'sourceLanguageCode': 'ko',
            'targetLanguageCode': lang,
            'texts': [ko_name],
        }
        encoder = json.encoder.JSONEncoder()
        payload = encoder.encode(payload)
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.ok:
            return response.json()['translations'][0]['text']
        else:
            raise ValueError('Ошибка подключения к переводчику')

    def book_registration(self, name, url) -> bool:
        with open(os.path.dirname(os.path.curdir).join('static').join('plug.jpg'), 'rb') as f:
            cover = f.read()
        data = {
            'csrfmiddlewaretoken': self.__get_csrf__(),
            'en_name': self.__translate_name__(name, 'en'),
            'rus_name': self.__translate_name__(name, 'ru'),
            'another_name': name,
            'description': '',
            'type': '1',
            'categories': '5',
            'genres': '2',
            'publishers': '6579',
            'status': '4',
            'age_limit': '0',
            'issue_year': '2021',
            'mangachan_link': '',
            'original_link': url,
            'anlate_link': '',
            'cover': cover,
            'readmanga_link': '',
            'user_message': '',
        }
        return self.__add_title__(data)

import json
import os
import sys

import requests
from bs4 import BeautifulSoup


class Registrar:
    name_filters = ('(연재)', '[연재]', '[만화]', '[코믹]', '(e-book)', '[웹툰]', '[웹툰판]', '(개정판)')

    def __init__(self, config):
        self.api_url = config['api_url']
        self.__token__ = None
        self.__user__ = None
        with open('registrar.txt', 'w', encoding='utf-8'):
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
        if response.status_code == 401 or response.status_code == 403:
            self.__authorize__()
            return self.__get_request__(url, data)
        return response

    def __authorize__(self):
        response = self.__post_request__('users/login/',
                                         {'user': os.getenv('REMANGA_USERNAME'),
                                          'password': os.getenv('REMANGA_PASSWORD')}).json()
        if response['content'] == []:
            raise ConnectionRefusedError(response['msg'])
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
        if response.status_code == 401 or response.status_code == 403:
            self.__authorize__()
            return self.__get_csrf__()
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
        files = {'cover': open(os.path.join(os.path.dirname(os.path.curdir), 'static', 'plug.jpg'), 'rb')}
        with open('registrar.txt', 'a', encoding='utf-8') as file:
            file.write(str(data) + '\n')
        if os.getenv('DEBUG') == 'False':
            response = requests.post('https://remanga.org/panel/add-titles/', headers=headers, data=data, files=files)
            if response.status_code == 401 or response.status_code == 403:
                self.__authorize__()
                return self.__add_title__(data)
            if response.text.find('Спасибо за помощь проекту, ваш запрос отправлен на модерацию', 1000, 10000) == -1:
                if response.text.find('Тайтл с таким') == -1:
                    return False
                else:
                    return True
            return response.ok
        else:
            return True

    def __translate_name__(self, ko_name: str, lang: str):
        for name_filter in self.name_filters:
            ko_name = ko_name.replace(name_filter, '')
        if sys.version_info.major == 3 and sys.version_info.minor >= 9:
            previous_name = ko_name
            while previous_name != ko_name:
                previous_name = ko_name
                ko_name = ko_name.removeprefix(' ').removesuffix(' ')
        if lang == 'ko':
            return ko_name
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

    def book_registration(self, url, name) -> bool:
        name = self.__translate_name__(name, 'ko')
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
            'readmanga_link': '',
            'user_message': '',
        }
        return self.__add_title__(data)

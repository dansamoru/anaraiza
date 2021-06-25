import time
import datetime
from json.decoder import JSONDecodeError

import requests

from modules.proxy import Proxy


class Website:
    def __init__(self, config, proxy_file_path):
        self.search_url = config['SEARCH_URL']
        self.subcategory = config['subcategory']
        self.proxy = Proxy(proxy_file_path=proxy_file_path)

    def __request__(self, page: int = 0) -> dict:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/88.0.4324.111 YaBrowser/21.2.1.94 (beta) Yowser/2.5 Safari/537.36',
        }
        while True:
            error_time = None
            # try:
            response = requests.get(self.search_url + '&issue_status=연재중%2C완결&subcategory_uid=' + self.subcategory,
                                    headers=headers,
                                    proxies={'https': str(self.proxy)})
            error_time = None
            if response.ok:
                response = response.json()
                if response['result_code'] == 0:
                    return response
            # except requests.exceptions.ConnectionError:
            #     self.proxy.next()
            # except ConnectionError:
            #     if error_time is None:
            #         error_time = time.time()
            #     if error_time is not None:
            #         if error_time - time.time() >= 300:
            #             self.proxy.next()

    def get_positions(self, page: int = 0):
        error_counter = 0
        while True:
            try:
                result = self.__request__(page=page)
                return result
            except JSONDecodeError:
                error_counter += 1
                if error_counter >= 10:
                    raise ConnectionError('Ошибка подключения к Kakao')

    def get_count(self) -> int:
        while True:
            try:
                result = self.__request__()
                return int(result['total_count'])
            except JSONDecodeError:
                raise ConnectionError('Ошибка подключения к Kakao')

    def update_proxy(self, val):
        self.proxy = val

import time
import datetime
from json.decoder import JSONDecodeError

import requests

from modules.proxy import Proxy


class Website:
    def __init__(self, config, proxy_file_path):
        self.url_address = config['BASE_URL']
        self.search_url = config['SEARCH_URL']
        self.search_request = config['SEARCH_REQUEST']
        self.proxy = Proxy(proxy_file_path=proxy_file_path)
        self.dynamic_date_search = config['DYNAMIC_DATE_SEARCH'] == 'True'

    def __request__(self, rows: int, start: int = 0, page: int = 1) -> requests.Response:
        fq_date: str = ''
        if self.dynamic_date_search:
            fq_date = 'PUBLISH_PREDATE : [' + (datetime.date.today() - datetime.timedelta(days=35)).strftime(
                '%Y/%m/%d') + ' TO ' + datetime.date.today().strftime('%Y/12/31') + ']'
        data = {
            'wt': 'json',
            'rows': rows,
            'start': start,
            'page': page,
            'tSrch_total': self.search_request,
            'fq_select': 'tSrc_total',
            'fq': fq_date,
            'detailSearchYn': 'Y',
        }
        while True:
            error_time = None
            try:
                response = requests.post(self.url_address + self.search_url, data=data,
                                         proxies={'http': str(self.proxy)})
                error_time = None
                if response.ok:
                    return response
            except requests.exceptions.ConnectionError:
                self.proxy.next()
            except ConnectionError:
                if error_time is None:
                    error_time = time.time()
                if error_time is not None:
                    if error_time - time.time() >= 300:
                        self.proxy.next()

    def get_positions(self, rows: int = None, start: int = 0, page: int = 1):
        if rows is None:
            rows = self.get_count()
        error_counter = 0
        while True:
            try:
                result = self.__request__(rows=rows, start=start, page=page).json()
                return result
            except JSONDecodeError:
                error_counter += 1
                if error_counter >= 10:
                    raise ConnectionError('Ошибка подключения к seoji')

    def get_count(self) -> int:
        error_counter = 0
        while True:
            try:
                result = self.__request__(rows=0)
                return int(result.json()['response']['numFound'])
            except JSONDecodeError:
                error_counter += 1
                if error_counter >= 10:
                    raise ConnectionError('Ошибка подключения к seoji')

    def update_proxy(self, val):
        self.proxy = val

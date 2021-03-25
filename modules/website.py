import time
import requests
from json.decoder import JSONDecodeError
from modules.proxy import Proxy


class Website:
    def __init__(self, config, proxy_file_path):
        self.url_address = config['URL_ADDRESS']
        self.search_request = config['SEARCH_REQUEST']
        self.proxy = Proxy(proxy_file_path=proxy_file_path)

    def __request__(self, rows: int, start: int = 0, page: int = 1) -> requests.Response:
        data = {
            'wt': 'json',
            'rows': rows,
            'start': start,
            'page': page,
            'tSrch_total': self.search_request,
            'fq_select': 'tSrc_total',
        }
        while True:
            error_time = None
            try:
                response = requests.post(self.url_address, data=data, proxies={'http': str(self.proxy)})
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
        while True:
            try:
                result = self.__request__(rows=rows, start=start, page=page).json()
                return result
            except JSONDecodeError:
                pass

    def get_count(self) -> int:
        while True:
            try:
                result = int(self.__request__(rows=0).json()['response']['numFound'])
                return result
            except JSONDecodeError:
                pass

    def update_proxy(self, val):
        self.proxy = val

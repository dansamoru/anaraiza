import csv
import time

import requests


class Proxy:
    def __init__(self, proxy_file_path):
        self.current_proxy = 1

        with open(proxy_file_path, 'r') as proxy_file:
            self.proxies = []
            proxy_reader = csv.reader(proxy_file, delimiter=';')
            for row in proxy_reader:
                self.proxies.append(['http://' + row[0] + ':' + row[1] + '@' + row[2] + ':' + row[3], 0.0])

    def __str__(self):
        return self.proxies[self.current_proxy][0]

    def next(self):
        print(time.strftime('[%X] ', time.localtime()) + '!   Запрос на изменение прокси   !')
        self.proxies[self.current_proxy][1] = time.time()
        enter_proxy = self.current_proxy
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)
        while time.time() - self.proxies[self.current_proxy][1] < 60:
            if self.current_proxy == enter_proxy:
                raise ConnectionError('Все прокси израсходованы. Добавьте новых или подождите')
            else:
                self.current_proxy = (self.current_proxy + 1) % len(self.proxies)


class Website:
    def __init__(self, url_address, search_request, proxy_file_path):
        self.url_address = url_address
        self.search_request = search_request
        self.proxy = Proxy(proxy_file_path=proxy_file_path)

    def __request__(self, rows: int, start: int = 0, page: int = 1) -> requests.Response:
        data = {
            'wt': 'json',
            'rows': rows,
            'start': start,
            'page': page,
            'tSrch_total': self.search_request,
            'fq_select': 'tSrc_total',
            'sort': 'PUBLISH_PREDATE ASC',
        }
        while True:
            try:
                response = requests.post(self.url_address, data=data, proxies={'http:': str(self.proxy)})
                # if not response.ok:
                #     raise ConnectionResetError('Ошибка подключения к сайту')
                return response
            except requests.exceptions.ProxyError:
                self.proxy.next()

    def get_positions(self, rows: int = None, start: int = 0, page: int = 1):
        if rows is None:
            rows = self.get_count()
        pos = self.__request__(rows=rows, start=start, page=page).json()
        return pos

    def get_count(self) -> int:
        return int(self.__request__(rows=0).json()['response']['numFound'])

    def update_proxy(self, val):
        self.proxy = val

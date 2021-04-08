import csv
import time


class Proxy:
    def __init__(self, proxy_file_path, delimiter=':', proxy_start: int = 0):
        with open(proxy_file_path, 'r', encoding='utf-8') as proxy_file:
            self.__proxies__ = []
            proxy_reader = csv.reader(proxy_file, delimiter=delimiter)
            for row in proxy_reader:
                if len(row) == 4:
                    self.__proxies__.append(['http://' + row[2] + ':' + row[3] + '@' + row[0] + ':' + row[1], 0.0])
                elif len(row) == 2:
                    self.__proxies__.append(['http://' + row[0] + ':' + row[1], 0.0])
                else:
                    raise ValueError('Некорректная запись адреса прокси')
            if proxy_start < len(self.__proxies__):
                self.__current_proxy__ = proxy_start
            else:
                raise ValueError('Номер первого прокси больше количества прокси')

    def __str__(self):
        return self.__proxies__[self.__current_proxy__][0]

    def next(self):
        self.__proxies__[self.__current_proxy__][1] = time.time()
        enter_proxy = self.__current_proxy__
        self.__current_proxy__ = (self.__current_proxy__ + 1) % len(self.__proxies__)
        while time.time() - self.__proxies__[self.__current_proxy__][1] < 60:
            if self.__current_proxy__ == enter_proxy:
                raise RuntimeError('Все прокси израсходованы. Добавьте новых или подождите')
            else:
                self.__current_proxy__ = (self.__current_proxy__ + 1) % len(self.__proxies__)

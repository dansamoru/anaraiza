import time
import csv


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
        # print(time.strftime('[%x %X] ', time.localtime()) + 'Получен запрос на изменение прокси')
        self.proxies[self.current_proxy][1] = time.time()
        enter_proxy = self.current_proxy
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)
        while time.time() - self.proxies[self.current_proxy][1] < 60:
            if self.current_proxy == enter_proxy:
                raise RuntimeError('Все прокси израсходованы. Добавьте новых или подождите')
            else:
                self.current_proxy = (self.current_proxy + 1) % len(self.proxies)
        # print(time.strftime('[%x %X] ', time.localtime()) + 'Установлен новый прокси: [' + str(
        #     self.current_proxy) + '] ' + str(self))

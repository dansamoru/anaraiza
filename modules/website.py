from json.decoder import JSONDecodeError
from bs4 import BeautifulSoup
import cloudscraper

import requests


class Website:
    def __init__(self, config):
        self.url_address = config['BASE_URL']
        self.search_url = config['SEARCH_URL']
        # self.search_request = config['SEARCH_REQUEST']
        # self.proxy = Proxy(proxy_file_path=proxy_file_path)
        # self.dynamic_date_search = config['DYNAMIC_DATE_SEARCH'] == 'True'

    def __request__(self) -> requests.Response:
        data = {
            #     'wt': 'json',
            #     'rows': rows,
            #     'start': start,
            #     'page': page,
            #     'tSrch_total': self.search_request,
            #     'fq_select': 'tSrc_total',
            #     'fq': fq_date,
            #     'detailSearchYn': 'Y',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ru,en;q=0.9',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.8.0.1967 (beta) Yowser/2.5 Safari/537.36',
            'cache-control': 'no-cache',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Yandex";v="92"',
            'cookie': '_ga=GA1.2.294598963.1631647379; _gid=GA1.2.1703054048.1632238869; __cf_bm=ZLfia.3F.x.R_9UpWNRAHQM3gJ3eDntA1pg7FhQxN_g-1632241072-0-AX/QPEYX73ealMljfHuiAg3BlrEun8tBnIfIHoFV+ltx8ozZCUqAlro7npnXH3//5zeU34l+712IMs3eneSCZoBvBEctHhHksd8UBOrg/w2jDExautEkVYYc2Ioy67KWTg==',
            'dnt': '1',
            'pragma': 'no-cache',
            'referer': 'https://www.novelupdates.com/',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        headers = {
            'report-to': '{"endpoints":[{"url":"https:\/\/a.nel.cloudflare.com\/report\/v3?s=%2F2KMBs36rLMD1y5I7M5x7L1CNxXbY9h6dQISona0zvfBIEDeHd0JZieYhPbY57vU1GuUx9JtlTSNlUZmkTniRHDrcwM3I%2FnvlQPZRCftDtT3%2FA2gQoidqSAcJGrsYS%2B88cGeQZGUjKhdrJnXdTqzJzft"}],"group":"cf-nel","max_age":604800}',
            'expect-ct': 'max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',

        }
        while True:
            # error_time = None
            # try:
            scraper = cloudscraper.create_scraper()
            # response = requests.post(self.url_address + self.search_url, data=data, headers=headers)
            response = scraper.get(self.url_address + self.search_url)
            # error_time = None
            if response.ok:
                return response
            # except requests.exceptions.ConnectionError:
            #     self.proxy.next()
            # except ConnectionError:
            #     if error_time is None:
            #         error_time = time.time()
            #     if error_time is not None:
            #         if error_time - time.time() >= 300:
            #             self.proxy.next()

    def get_positions(self):
        # error_counter = 0
        while True:
            # try:
            result = []
            soup = BeautifulSoup(self.__request__().text, 'html.parser')
            for data in soup.find_all(class_='search_title'):
                for child in data.children:
                    if 'href' in child.attrs:
                        result.append(child.attrs['href'])
            return result
        # except JSONDecodeError:
        #     error_counter += 1
        #     if error_counter >= 10:
        #         raise ConnectionError('Ошибка подключения к novelupdates')

    # def get_count(self) -> int:
    #     error_counter = 0
    #     while True:
    #         try:
    #             result = self.__request__(rows=0)
    #             return int(result.json()['response']['numFound'])
    #         except JSONDecodeError:
    #             error_counter += 1
    #             if error_counter >= 10:
    #                 raise ConnectionError('Ошибка подключения к seoji')

    # def update_proxy(self, val):
    #     self.proxy = val

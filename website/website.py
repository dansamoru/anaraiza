import requests


class Website:
    def __init__(self, url_address, search_request, proxy):
        self.url_address = url_address
        self.search_request = search_request
        self.proxy = proxy

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
        return requests.post(self.url_address, data=data, proxies=self.proxy)

    def get_positions(self, rows: int = None, start: int = 0, page: int = 1):
        if rows is None:
            rows = self.get_count()
        return self.__request__(rows=rows, start=start, page=page).json()

    def get_count(self) -> int:
        return int(self.__request__(rows=0).json()['response']['numFound'])

    def update_proxy(self, val):
        self.proxy = val

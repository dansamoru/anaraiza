import requests


class Website:
    def __init__(self, url_address, search_request):
        self.url_address = url_address
        self.search_request = search_request

    def __request__(self, rows: int, start: int = 0, page: int = 1) -> requests.Response:
        data = {
            'wt': 'json',
            'rows': rows,
            'start': start,
            'page': page,
            'tSrch_total': self.search_request,
            'fq_select': 'tSrc_total',
        }
        return requests.post(self.url_address, data=data)

    def get_positions(self, rows: int, start: int = 0, page: int = 1):
        return self.__request__(rows=rows, start=start, page=page).json()

    def get_count(self):
        return self.__request__(rows=0).json()

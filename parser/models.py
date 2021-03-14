import requests
import sqlite3
import csv


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


class Database:
    def __init__(self, database_file):
        self.name = 'books'
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
        self.__create__()
        self.edited = True
        self.item_amount = self.count()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def __create__(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (key INT UNIQUE, isbn INT)''')

    def __insert__(self, key: int, isbn: int) -> bool:
        try:
            self.cursor.execute('''INSERT INTO books values(?, ?)''', (key, isbn))
        except sqlite3.IntegrityError:
            return False
        else:
            self.edited = True
            return True

    def reload(self, data):
        self.cursor.execute('''DROP TABLE books''')
        self.__create__()
        self.insert_many(data)

    def count(self) -> int:
        if self.edited:
            self.cursor.execute('''SELECT COUNT(*) FROM books''')
            self.item_amount = int(self.cursor.fetchone()[0])
            self.edited = False
        return self.item_amount

    def insert_many(self, array):
        for element in array:
            self.__insert__(element[0], element[1])

    def is_unique(self, key: int, isbn: int) -> bool:
        return self.__insert__(key=key, isbn=isbn)


class OutputWriter:
    def __init__(self, output_file_path, output_file_mode, url, output_find_text):
        self.output_file_path = output_file_path
        self.output_file_mode = output_file_mode
        self.url = url
        self.output_find_text = output_find_text
        self.queue = []

    def add_book(self, isbn: int):
        self.queue.append(self.output_find_text + str(self.url) + str(isbn) + '\n')

    def write(self):
        with open(self.output_file_path, self.output_file_mode) as output_file:
            for element in self.queue:
                output_file.write(element)


class Proxy:
    def __init__(self, proxy_file_path):
        self.current_proxy = 0

        with open(proxy_file_path, 'r') as proxy_file:
            self.proxies = []
            proxy_reader = csv.reader(proxy_file, delimiter=';')
            for row in proxy_reader:
                self.proxies.append('http://' + row[0] + ':' + row[1] + '@' + row[2] + ':' + row[3])

    def __str__(self):
        return self.proxies[self.current_proxy]

    def change(self):
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)

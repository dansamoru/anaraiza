import requests
import sqlite3


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


class Database:
    def __init__(self, database_file):
        self.name = 'books'
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
        self.__create__()

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
            return True

    def reload(self, data):
        self.cursor.execute('''DROP TABLE books''')
        self.__create__()
        self.insert_many(data)

    def count(self) -> int:
        self.cursor.execute('''SELECT COUNT(*) FROM books''')
        return int(self.cursor.fetchone()[0])

    def insert_many(self, array):
        for element in array:
            self.__insert__(element[0], element[1])

    def is_unique(self, key: int, isbn: int) -> bool:
        return self.__insert__(key=key, isbn=isbn)

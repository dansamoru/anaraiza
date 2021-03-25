import sqlite3


class Database:
    def __init__(self, database_file):
        self.name = 'books'
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
        self.__create__()
        self.edited = True
        self.item_amount = self.count()

    def __del__(self):
        self.commit()
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

    def commit(self):
        self.connection.commit()

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

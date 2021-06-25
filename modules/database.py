import sqlite3


class Database:
    def __init__(self, config):
        self.name = 'books'
        self.connection = sqlite3.connect(config['DATABASE_FILE_PATH'])
        self.cursor = self.connection.cursor()
        self.__create__()
        self.item_amount = 0

    def __del__(self):
        self.commit()
        self.connection.close()

    def __create__(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (identifier INT UNIQUE)''')

    def __insert__(self, identifier: int) -> bool:
        try:
            self.cursor.execute('''INSERT INTO books values (?)''', (identifier,))
        except sqlite3.IntegrityError:
            return False
        else:
            return True

    def drop(self):
        self.cursor.execute('''DROP TABLE books''')

    def commit(self):
        self.connection.commit()

    def reload(self, data):
        self.drop()
        self.__create__()
        self.insert_many(data)
        self.commit()

    def count(self) -> int:
        return self.item_amount

    def set_amount(self, amount: int) -> None:
        self.item_amount = amount

    def insert_many(self, array):
        for element in array:
            self.__insert__(element)
        self.cursor.execute('''SELECT COUNT(*) FROM books''')
        self.item_amount = int(self.cursor.fetchone()[0])
        self.commit()

    def is_unique(self, identifier: int) -> bool:
        if self.__insert__(identifier=identifier):
            self.item_amount += 1
            return True
        else:
            return False

    def remove(self, identifier: int):
        self.cursor.execute('''DELETE FROM BOOKS WHERE identifier = "%s"''' % str(identifier))
        self.commit()

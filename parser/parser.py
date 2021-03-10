import time

from models import *
from settings import *

website = Website(url_address=URL_ADDRESS, search_request=SEARCH_REQUEST)
database = Database(database_file=DATABASE_FILE_PATH)


def write_new_positions(data):
    with open(OUTPUT_FILE_PATH, 'a') as output_file:
        for item in data:
            output_file.write(item[0] + ' ' + item[1] + '\n')


def check():
    website_count = website.get_count()
    database_count = database.count()
    if website_count > database_count:
        success = True
        new_positions = set()
        positions = website.get_positions(website_count - database_count)
        for doc in positions['response']['docs']:
            if success:
                if database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                    new_positions.add((doc['REC_KEY'], doc['EA_ISBN']))
                else:
                    success = False
        if not success:
            new_positions.clear()
            positions = website.get_positions()
            for doc in positions['response']['docs']:
                if database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                    new_positions.add((doc['REC_KEY'], doc['EA_ISBN']))


def init():
    website_count = website.get_count()
    database_count = database.count()
    if website_count != database_count:
        positions = website.get_positions(website_count)
        data = []
        for doc in positions['response']['docs']:
            data.append((doc['REC_KEY'], doc['EA_ISBN']))
        database.reload(data)


if __name__ == '__main__':
    init()
    start_time = time.time()
    last_time = start_time
    check_counter = 0
    while True:
        check()
        check_counter += 1
        current_time = time.time()
        print('Время выполнения последней итерации: ' +
              f'{str((current_time - last_time)):.{10}}' + ' секунд')
        if check_counter % 50 == 0:
            print('Среднее время выполнения за [' +
                  str(check_counter) + '] итераций: ' +
                  f'{str((current_time - start_time) / check_counter):.{10}}' + ' секунд')
        last_time = current_time

import time

from models import *
from settings import *

proxy = Proxy(proxy_file_path=PROXY_FILE_PATH)

website = Website(url_address=BASE_URL + SEARCH_URL,
                  search_request=SEARCH_REQUEST,
                  proxy={'http': str(proxy)})

database = Database(database_file=DATABASE_FILE_PATH)

writer = OutputWriter(output_file_path=OUTPUT_FILE_PATH,
                      output_file_mode=OUTPUT_FILE_MODE,
                      url=BASE_URL + VIEW_URL,
                      output_find_text=OUTPUT_FIND_TEXT)


def check():
    website_count = website.get_count()
    database_count = database.count()
    if website_count > database_count:
        success = True
        positions = website.get_positions(website_count - database_count)['response']['docs']
        positions.reverse()
        for doc in positions:
            if success:
                if database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                    writer.add_book(doc['EA_ISBN'])
                else:
                    success = False
        if not success:
            positions = website.get_positions()
            database.insert_many((doc['REC_KEY'], doc['EA_ISBN']) for doc in positions['response']['docs'].reverse())
        writer.write()
    elif website_count < database_count:
        positions = website.get_positions(website_count)['response']['docs']
        positions.reverse()
        data = []
        for doc in positions:
            data.append((doc['REC_KEY'], doc['EA_ISBN']))
        database.reload(data)


if __name__ == '__main__':
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

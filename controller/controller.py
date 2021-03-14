import time
import os

from database.database import Database
from website.website import Website
from website.models.proxy import Proxy
from telegram.telegram import Telegram


class Controller:
    def __init__(self, config):
        self.proxy = Proxy(proxy_file_path=config['Proxy']['PROXY_FILE_PATH'])

        self.website = Website(url_address=config['Website']['BASE_URL'] + config['Website']['SEARCH_URL'],
                               search_request=config['Website']['SEARCH_REQUEST'],
                               proxy={'http': str(self.proxy)})

        self.database = Database(database_file=config['Database']['DATABASE_FILE_PATH'])

        self.telegram = Telegram(bot_token=os.environ.get('TELEGRAM_BOT_TOKEN'),
                                 chat_id=os.environ.get('TELEGRAM_CHAT_ID'))
        self.view_url = config['Website']['base_url'] + config['Website']['view_url']

    def check(self):
        website_count = self.website.get_count()
        database_count = self.database.count()
        if database_count == 0 or website_count < database_count:
            positions = self.website.get_positions(website_count)['response']['docs']
            positions.reverse()
            data = []
            for doc in positions:
                data.append((doc['REC_KEY'], doc['EA_ISBN']))
            self.database.reload(data)
        elif website_count > database_count:
            success = True
            positions = self.website.get_positions(website_count - database_count)['response']['docs']
            positions.reverse()
            for doc in positions:
                if success:
                    if self.database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                        self.telegram.write('Найден новый элемент: ' + self.view_url + doc['EA_ISBN'])
                    else:
                        success = False
            if not success:
                positions = self.website.get_positions()
                self.database.insert_many(
                    (doc['REC_KEY'], doc['EA_ISBN']) for doc in positions['response']['docs'].reverse())

    def start(self):
        start_time = time.time()
        last_time = start_time
        check_counter = 0
        while True:
            self.check()
            check_counter += 1
            current_time = time.time()
            print('Время выполнения последней итерации: ' +
                  f'{str((current_time - last_time)):.{10}}' + ' секунд')
            if check_counter % 50 == 0:
                print('Среднее время выполнения за [' +
                      str(check_counter) + '] итераций: ' +
                      f'{str((current_time - start_time) / check_counter):.{10}}' + ' секунд')
            last_time = current_time

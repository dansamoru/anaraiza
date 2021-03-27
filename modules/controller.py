import os
import traceback

from modules.database import Database
from modules.telegram import Telegram
from modules.website import Website


class Controller:
    def __init__(self, config):
        self.website = Website(config['Website'],
                               proxy_file_path=config['Proxy']['PROXY_FILE_PATH'])

        self.database = Database(config['Database'])

        self.telegram = Telegram(bot_token=os.environ.get('TELEGRAM_BOT_TOKEN'),
                                 chat_id=os.environ.get('TELEGRAM_CHAT_ID'))

        self.view_url = config['Website']['base_url'] + config['Website']['view_url']

    def update(self):
        website_count = self.website.get_count()
        database_count = self.database.count()
        if database_count == 0 or website_count < database_count:
            positions = self.website.get_positions(website_count)['response']['docs']
            data = []
            for doc in positions:
                data.append((doc['REC_KEY'], doc['EA_ISBN']))
            self.database.reload(data)
        elif website_count > database_count:
            positions = self.website.get_positions(website_count)['response']['docs']
            for doc in positions:
                if self.database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                    self.telegram.write('Найден новый элемент: ' + self.view_url + doc['EA_ISBN'])
                    # print(time.strftime('[%x %X] ', time.localtime()) + 'Обнаружен новый элемент')

    def start(self):
        # start_time = time.time()
        # last_time = start_time
        update_counter = 0
        # print(time.strftime('[%x %X] ', time.localtime()) + 'Начало выполнения')
        while True:
            try:
                self.update()
            except Exception as exception:
                self.telegram.write(
                    'Поздравляю! Случилась ошибка 🥰\n\n⚠ : ' + str(traceback.format_exc()))
                raise exception
            update_counter += 1
            # current_time = time.time()
            # print(time.strftime('[%x %X] ', time.localtime()) + 'Время выполнения последней итерации: ' +
            #       f'{str((current_time - last_time)):.{10}}' + ' секунд')
            # if update_counter % 50 == 0:
            #     print(time.strftime('[%x %X] ', time.localtime()) + 'Среднее время выполнения за [' +
            #           str(update_counter) + '] итераций: ' +
            #           f'{str((current_time - start_time) / update_counter):.{10}}' + ' секунд')
            if update_counter % 50000 == 0:
                self.database.commit()
                update_counter %= 50000
            # last_time = current_time

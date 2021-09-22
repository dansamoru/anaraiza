import os
import traceback

from modules.telegram import Telegram
from modules.website import Website

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Controller:
    # STEP = 100

    def __init__(self, config):
        self.website = Website(config['Website'])

        self.database = []

        self.telegram = Telegram(bot_token=os.environ.get('TELEGRAM_BOT_TOKEN'),
                                 chat_id={'prod-main': os.environ.get('TELEGRAM_CHAT_ID_PROD_MAIN'),
                                          'prod-dev': os.environ.get('TELEGRAM_CHAT_ID_PROD_DEV'),
                                          'debug-all': os.environ.get('TELEGRAM_CHAT_ID_DEBUG_ALL'), }
                                 )

        # self.registrar = Registrar(config['noveupdates'])

        self.view_url = config['Website']['base_url'] + config['Website']['view_url']

        # self.is_database_filled = False

    # def __del__(self):
        # if not self.is_database_filled:
        #     self.database.drop()

    def __database_filling__(self):
        # start_count = 0
        # len_count = website_count - start_count
        # if len_count > self.STEP:
        #     len_count = self.STEP
        # data = []
        # while start_count + len_count <= website_count:
        #     positions = self.website.get_positions(rows=len_count, start=start_count)['response']['docs']
        #     for doc in positions:
        #         data.append((doc['REC_KEY'], doc['EA_ISBN']))
        #     start_count += self.STEP
        #     len_count = website_count - start_count
        #     if len_count > self.STEP or len_count < 0:
        #         len_count = self.STEP
        #     if os.getenv('DEBUG') == 'True':
        #         print('Filling database... (' + str(start_count) + '/' + str(website_count) + ')  -  ' + str(
        #             start_count / website_count * 100)[:4:] + '%')
        # self.database.reload(data)
        self.database = self.website.get_positions()

    def book_registration_notifier(self, url):
        message = '✅ Новый элемент: \n\n' + url
        self.telegram.write(message, 'prod-main')

    def book_registration(self, url):
        # self.registrar.book_registration(tag)
        self.database.append(url)
        self.book_registration_notifier(url)

    def update(self):
        # website_count = self.website.get_count()
        database_count = len(self.database)
        if database_count == 0:
            # self.is_database_filled = False
            self.__database_filling__()
            # self.is_database_filled = True
        # elif database_count < website_count:
        #     start_count = 0
        #     len_count = website_count - start_count
        #     if len_count > self.STEP:
        #         len_count = self.STEP
        #     while start_count + len_count <= website_count and len_count >= 0:
        positions = self.website.get_positions()
        for doc in positions:
            if doc not in self.database:
                self.book_registration(doc)
                # start_count += self.STEP
            #     len_count = website_count - start_count
            #     if len_count > self.STEP:
            #         len_count = self.STEP
            # self.database.commit()

    def start(self):
        is_start = True
        while True:
            try:
                if is_start:
                    self.telegram.write('Module launched', tag='prod-dev')
                self.update()
                # self.database.remove('https://www.novelupdates.com/series/my-ex-boyfriend-became-my-current-teammate/')
                if is_start:
                    self.telegram.write('Module started', tag='prod-dev')
                is_start = False
            except Exception as exception:
                with open('error.txt', 'w') as error_file:
                    error_file.write(traceback.format_exc())
                self.telegram.write(
                    'Поздравляю! Случилась ошибка 🥰\n\n⚠ : ' + str(exception), 'prod-dev')
                os.system(os.path.join(BASE_PATH, 'start.sh'))
                raise exception

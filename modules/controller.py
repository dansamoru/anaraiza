import os
import traceback

from modules.database import Database
from modules.registrar import Registrar
from modules.telegram import Telegram
from modules.website import Website

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Controller:
    STEP = 100

    def __init__(self, config):
        self.website = Website(config['Website'],
                               proxy_file_path=config['Proxy']['PROXY_FILE_PATH'])

        self.database = Database(config['Database'])

        self.telegram = Telegram(bot_token=os.environ.get('TELEGRAM_BOT_TOKEN'),
                                 chat_id={'prod-main': os.environ.get('TELEGRAM_CHAT_ID_PROD_MAIN'),
                                          'prod-dev': os.environ.get('TELEGRAM_CHAT_ID_PROD_DEV'),
                                          'debug-all': os.environ.get('TELEGRAM_CHAT_ID_DEBUG_ALL'), }
                                 )

        self.registrar = Registrar(config['Remanga'])

        self.view_url = config['Website']['base_url'] + config['Website']['view_url']

        self.is_database_filled = False

    def __del__(self):
        if not self.is_database_filled:
            self.database.drop()

    def __database_filling__(self, website_count: int):
        start_count = 0
        len_count = website_count - start_count
        if len_count > self.STEP:
            len_count = self.STEP
        data = []
        while start_count + len_count <= website_count:
            positions = self.website.get_positions(rows=len_count, start=start_count)['response']['docs']
            for doc in positions:
                data.append((doc['REC_KEY'], doc['EA_ISBN']))
            start_count += self.STEP
            len_count = website_count - start_count
            if len_count > self.STEP or len_count < 0:
                len_count = self.STEP
            if os.getenv('DEBUG') == 'True':
                print('Filling database... (' + str(start_count) + '/' + str(website_count) + ')  -  ' + str(
                    start_count / website_count * 100)[:4:] + '%')
        self.database.reload(data)

    def book_registration_notifier(self, key, isbn, name, success: bool = True):
        message = 'Новый элемент: \n' + name + '\n' + (self.view_url + isbn) + '\n\n' + '✅ Найден'
        if success:
            message += '\n✅ Зарегистрирован'
        else:
            message += '\n❌ Зарегистрирован'
            self.database.remove(key)
            message += '\n✅ Удалён из базы данных'
        self.telegram.write(message, 'prod-main')

    def book_registration(self, name, key, isbn):
        try:
            success = self.registrar.book_registration(self.view_url + isbn, name)
        except Exception as exception:
            self.book_registration_notifier(key, isbn, name, False)
            raise exception
        self.book_registration_notifier(key, isbn, name, success)

    def update(self, is_first_update):
        website_count = self.website.get_count()
        database_count = self.database.count()
        if database_count == 0 or website_count < database_count:
            self.is_database_filled = False
            self.__database_filling__(website_count)
            self.is_database_filled = True
        elif database_count < website_count:
            start_count = 0
            len_count = website_count - start_count
            if len_count > self.STEP:
                len_count = self.STEP
            while start_count + len_count < website_count:
                positions = self.website.get_positions(rows=len_count, start=start_count)['response']['docs']
                for doc in positions:
                    if self.database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                        if not is_first_update:
                            self.book_registration(doc['TITLE'], doc['REC_KEY'], doc['EA_ISBN'])
                start_count += self.STEP
                len_count = website_count - start_count
                if len_count > self.STEP:
                    len_count = self.STEP
            self.database.commit()

    def start(self):
        is_start = True
        while True:
            try:
                if is_start:
                    self.telegram.write('Module launched', tag='prod-dev')
                self.update(is_start)
                if is_start:
                    self.telegram.write('Module started', tag='prod-dev')
                is_start = False
            except Exception as exception:
                with open('error.txt', 'w') as error_file:
                    error_file.write(traceback.format_exc())
                self.telegram.write(
                    'Поздравляю! Случилась ошибка 🥰\n\n⚠ : ' + str(exception), 'prod-dev')
                #  os.system(os.path.join(BASE_PATH, 'start.sh'))
                raise exception

import datetime
import os
import traceback

from modules.database import Database
from modules.registrar import Registrar
from modules.telegram import Telegram
from modules.website import Website

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Controller:
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

        self.view_url = config['Website']['view_url']
        self.update_time: int = int(config['Controller']['update_time'])

        self.is_database_filled = True

    def __del__(self):
        if not self.is_database_filled:
            self.database.drop()

    def __database_filling__(self):
        data = []
        positions = self.website.get_positions()['data']
        for doc in positions:
            data.append(doc['season_id'])
        self.database.reload(data)

    def book_registration_notifier(self, title, identifier, success: bool = True):
        message = 'Новый элемент: \n' + title + '\n' + (self.view_url + str(identifier)) + '\n\n' + '✅ Найден'
        if success:
            message += '\n✅ Зарегистрирован'
        else:
            message += '\n❌ Зарегистрирован'
            self.database.remove(identifier)
            message += '\n✅ Удалён из базы данных'
        self.telegram.write(message, 'prod-main')

    def book_registration(self, title: str, identifier: int, image_url: str):
        try:
            success = self.registrar.book_registration(self.view_url + str(identifier), title, image_url)
        except Exception as exception:
            self.book_registration_notifier(title, identifier, False)
            raise exception
        if not success:
            self.database.remove(identifier=identifier)
        self.book_registration_notifier(title, identifier, success)

    def update(self, is_first_update):
        database_count = self.database.count()
        if database_count == 0:
            self.is_database_filled = False
            self.__database_filling__()
            self.is_database_filled = True
        positions = self.website.get_positions()['data']
        if not is_first_update:
            for doc in positions:
                if self.database.is_unique(doc['season_id']):
                    self.book_registration(doc['title'], int(doc['season_id']), doc['square_cover'])
        self.database.commit()

    def clear(self):
        for file in os.listdir(os.path.join(os.path.dirname(os.path.curdir), 'cache')):
            if str(file) != '.gitkeep':
                os.remove(os.path.join(os.path.dirname(os.path.curdir), 'cache', file))

    def start(self):
        is_start = False
        last_time = datetime.datetime.now()
        while True:
            if datetime.datetime.now() - last_time >= datetime.timedelta(seconds=self.update_time) or is_start:
                try:
                    if is_start:
                        self.telegram.write('Module launched', tag='prod-dev')
                    self.update(is_start)
                    last_time = datetime.datetime.now()
                    self.clear()
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

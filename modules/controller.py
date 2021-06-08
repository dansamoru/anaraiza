import os
import traceback

from modules.database import Database
from modules.registrar import Registrar
from modules.telegram import Telegram
from modules.website import Website

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


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

        self.view_url = config['Website']['base_url'] + config['Website']['view_url']

    def book_registration(self, url, name):
        if self.registrar.book_registration(name, url):
            self.telegram.write('Зарегистрирован новый элемент 😎: \n' + name + '\n\n' + url, 'prod-main')
        else:
            self.telegram.write('Ошибка регистрации 🤫: \n' + name + '\n\n' + url, 'prod-dev')

    def update(self, is_first_update):
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
                    if not is_first_update:
                        self.telegram.write(
                            'Найден новый элемент: \n' + doc['TITLE'] + '\n\n' + self.view_url + doc['EA_ISBN'],
                            'prod-main')
                        self.book_registration(self.view_url + doc['EA_ISBN'], doc['TITLE'])
            self.database.commit()

    def start(self):
        is_start = True
        while True:
            try:
                self.update(is_start)
                if is_start and os.environ.get('DEBUG') == 'True':
                    self.telegram.write('Module (re)started', tag='prod_dev') 
                is_start = False
            except Exception as exception:
                with open('error.txt', 'w') as error_file:
                    error_file.write(traceback.format_exc())
                self.telegram.write(
                    'Поздравляю! Случилась ошибка 🥰\n\n⚠ : ' + str(exception), 'prod-dev')
                os.path.join(BASE_PATH, 'start.sh')
                raise exception

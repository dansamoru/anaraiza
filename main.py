import configparser
import os

import dotenv

from modules import controller

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(BASE_PATH, 'config.ini')


def load_env():
    env_file_path = os.path.join(BASE_PATH, '.env')
    if os.environ.get('TELEGRAM_BOT_TOKEN') is None or os.environ.get('TELEGRAM_CHAT_ID') is None:
        if os.path.exists(env_file_path):
            dotenv.load_dotenv(env_file_path)
        else:
            raise FileNotFoundError('Файл переменных окружения не найден')


def load_config(config_file_path):
    if os.path.exists(config_file_path):
        input_config = configparser.ConfigParser()
        input_config.read(config_file_path, encoding='utf-8')
        return input_config
    else:
        raise FileNotFoundError('Файл настроек не найден')


if __name__ == '__main__':
    config = load_config(CONFIG_FILE_PATH)
    load_env()
    controller = controller.Controller(config)
    controller.start()

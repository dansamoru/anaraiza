import os


#  ---  Global  ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


#  ---  Website  ---
BASE_URL = 'http://seoji.nl.go.kr/landingPage'
SEARCH_URL = '/SearchList.do'
VIEW_URL = '?isbn='
SEARCH_REQUEST = '(연재) 원작자 2021'


#  ---  Database  ---
DATABASE_FILE_PATH = os.path.join(BASE_DIR, 'database.sqlite')


#  ---  Output  ---
OUTPUT_FILE_PATH = os.path.join(BASE_DIR, 'output.txt')
OUTPUT_FILE_MODE = 'a'
OUTPUT_FIND_TEXT = 'Найден новый файл! '

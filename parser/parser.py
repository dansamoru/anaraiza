from database.database import Database
from website.website import Website
from writer.writer import OutputWriter
from website.models.proxy import Proxy
from settings import *


class Controller:
    def __init__(self):
        self.proxy = Proxy(proxy_file_path=PROXY_FILE_PATH)

        self.website = Website(url_address=BASE_URL + SEARCH_URL,
                               search_request=SEARCH_REQUEST,
                               proxy={'http': str(self.proxy)})

        self.database = Database(database_file=DATABASE_FILE_PATH)

        self.writer = OutputWriter(output_file_path=OUTPUT_FILE_PATH,
                                   output_file_mode=OUTPUT_FILE_MODE,
                                   url=BASE_URL + VIEW_URL,
                                   output_find_text=OUTPUT_FIND_TEXT)

    def check(self):
        website_count = self.website.get_count()
        database_count = self.database.count()
        if website_count > database_count:
            success = True
            positions = self.website.get_positions(website_count - database_count)['response']['docs']
            positions.reverse()
            for doc in positions:
                if success:
                    if self.database.is_unique(doc['REC_KEY'], doc['EA_ISBN']):
                        self.writer.add_book(doc['EA_ISBN'])
                    else:
                        success = False
            if not success:
                positions = self.website.get_positions()
                self.database.insert_many(
                    (doc['REC_KEY'], doc['EA_ISBN']) for doc in positions['response']['docs'].reverse())
            self.writer.write()
        elif website_count < database_count:
            positions = self.website.get_positions(website_count)['response']['docs']
            positions.reverse()
            data = []
            for doc in positions:
                data.append((doc['REC_KEY'], doc['EA_ISBN']))
            self.database.reload(data)

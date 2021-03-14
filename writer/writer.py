class OutputWriter:
    def __init__(self, output_file_path, output_file_mode, url, output_find_text):
        self.output_file_path = output_file_path
        self.output_file_mode = output_file_mode
        self.url = url
        self.output_find_text = output_find_text
        self.queue = []

    def add_book(self, isbn: int):
        self.queue.append(self.output_find_text + str(self.url) + str(isbn) + '\n')

    def write(self):
        with open(self.output_file_path, self.output_file_mode) as output_file:
            for element in self.queue:
                output_file.write(element)

class Proxy:
    def __init__(self, proxy_file_path):
        self.current_proxy = 0

        with open(proxy_file_path, 'r') as proxy_file:
            self.proxies = []
            proxy_reader = csv.reader(proxy_file, delimiter=';')
            for row in proxy_reader:
                self.proxies.append('http://' + row[0] + ':' + row[1] + '@' + row[2] + ':' + row[3])

    def __str__(self):
        return self.proxies[self.current_proxy]

    def change(self):
        self.current_proxy = (self.current_proxy + 1) % len(self.proxies)

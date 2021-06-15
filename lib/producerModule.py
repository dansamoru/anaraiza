from baseModule import BaseModule
import pika


class ProducerModule(BaseModule):
    def __init__(self, connection_parameters='localhost', queue='default'):
        super().__init__()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(connection_parameters))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)

    def __del__(self):
        self.connection.close()

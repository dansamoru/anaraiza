from baseModule import BaseModule
import pika


class ConsumerModule(BaseModule):
    def __init__(self, connection_parameters='localhost', queue='default'):
        super().__init__()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(connection_parameters))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_consume(queue=queue,
                                   auto_ack=True,
                                   on_message_callback=self.callback)
        self.channel.start_consuming()

    def __del__(self):
        self.connection.close()

    def callback(self, channel, method, properties, body):
        print('received %r' % body)

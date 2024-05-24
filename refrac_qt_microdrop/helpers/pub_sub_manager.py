import threading

import pika
from typing import Callable, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class PubSubManager:
    def __init__(self):
        self.publishers = {}
        self.subscribers = {}
        self.info_to_start_consumer = {}

    def create_publisher(self, publisher_name: str, exchange_name: str):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        self.publishers[publisher_name] = (connection, channel, exchange_name)
        print(f"created {publisher_name} for {exchange_name}")
        logger.info(f"Publisher {publisher_name} created for exchange {exchange_name}")

    def publish(self, message: BaseModel, publisher: str):
        if publisher in self.publishers:
            connection, channel, exchange_name = self.publishers[publisher]
            channel.basic_publish(
                exchange=exchange_name,
                routing_key='',
                body=message.model_dump_json()
            )
            print(f"Published message: {message.model_dump_json()} to {exchange_name}")
            logger.info(f"Published message: {message.model_dump_json()} to {exchange_name}")
        else:
            logger.error(f"Publisher {publisher} not found")

    def create_subscriber(self, subscriber_name: str):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        self.subscribers[subscriber_name] = (connection, channel)
        print(f"Subscriber {subscriber_name} created")
        logger.info(f"Subscriber {subscriber_name} created")

    def bind_sub_to_pub(self, subscriber: str, exchange_name: str):
        if subscriber in self.subscribers:
            _, sub_channel = self.subscribers[subscriber]
            result = sub_channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            sub_channel.queue_bind(exchange=exchange_name, queue=queue_name)
            logger.info(f"Subscriber {subscriber} bound to exchange {exchange_name} on queue {queue_name}")
            print(f"Subscriber {subscriber} bound to exchange {exchange_name} on queue {queue_name}")
            self.info_to_start_consumer[subscriber] = (sub_channel, queue_name)
        else:
            logger.error(f"Subscriber {subscriber} not found")

    def start_consumer(self, subscriber: str, func: Callable[[Any, Any, Any, Any], None]):
        print("Attempting to start consumer")
        if subscriber not in self.info_to_start_consumer:
            logger.error(f"Subscriber {subscriber} not found")
            raise ValueError(f"Subscriber {subscriber} not found")

        sub_channel, queue_name = self.info_to_start_consumer[subscriber]
        print(f"Starting consumer for {subscriber} on {queue_name} via {sub_channel}")
        print(f"Attempting to consume message on {queue_name} with {func}")

        def consumer_thread():
            sub_channel.basic_consume(queue=queue_name, on_message_callback=func, auto_ack=False)
            logger.info(f"Starting consumer for subscriber {subscriber}")
            sub_channel.start_consuming()
            print("Started consuming")

        thread = threading.Thread(target=consumer_thread)
        thread.start()
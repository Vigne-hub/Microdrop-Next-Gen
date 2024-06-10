import threading
import pika
from pydantic import BaseModel
from traits.api import Dict, Callable, Any, HasTraits, provides
from traits.trait_types import Str

from ..interfaces.i_pub_sub_manager_service import IPubSubManagerService
from ..utils.logger import initialize_logger

logger = initialize_logger(__name__)


@provides(IPubSubManagerService)
class PubSubManager(HasTraits):
    """
    PubSubManager class to manage publishers and subscribers
    """
    id = Str("pub_sub_manager")
    name = Str("PubSub Manager")

    publishers = Dict(desc="Publishers")
    subscribers = Dict(desc="Subscribers")
    info_to_start_consumer = Dict(desc="Information required to start a consumer")

    def create_publisher(self, publisher_name: str, exchange_name: str):
        """
        Create a publisher for a given exchange
        :param publisher_name: name of the publisher
        :param exchange_name: rabbitmq exchange name
        :return: None
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
        self.publishers[publisher_name] = (connection, channel, exchange_name)

        logger.info(f"Publisher {publisher_name} created for exchange {exchange_name}")

    def publish(self, message: BaseModel, publisher: str):
        """
        Publish a message to a given exchange
        :param message:
        :param publisher:
        :return:
        """

        if publisher in self.publishers:
            connection, channel, exchange_name = self.publishers[publisher]
            channel.basic_publish(
                exchange=exchange_name,
                routing_key='',
                body=message.model_dump_json()
            )

            logger.info(f"Published message: {message.model_dump_json()} to {exchange_name}")

        else:
            logger.error(f"Publisher {publisher} not found")
            raise KeyError(f"Publisher {publisher} not found")

    def create_subscriber(self, subscriber_name: str):
        """
        Create a subscriber
        :param subscriber_name:
        :return:
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        self.subscribers[subscriber_name] = (connection, channel)

        logger.info(f"Subscriber {subscriber_name} created")

    def bind_sub_to_pub(self, subscriber: str, exchange_name: str):
        """
        Bind a subscriber to a publisher
        :param subscriber:
        :param exchange_name:
        :return:
        """
        if subscriber in self.subscribers:
            _, sub_channel = self.subscribers[subscriber]
            result = sub_channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            sub_channel.queue_bind(exchange=exchange_name, queue=queue_name)

            logger.info(f"Subscriber {subscriber} bound to exchange {exchange_name} on queue {queue_name}")

            self.info_to_start_consumer[subscriber] = (sub_channel, queue_name)
        else:
            logger.error(f"Subscriber {subscriber} not found")
            raise KeyError(f"Subscriber {subscriber} not found")

    def start_consumer(self, subscriber: str, func: Callable(Any)):
        """ Method to Start the consumer"""
        if subscriber not in self.info_to_start_consumer:
            logger.error(f"Subscriber {subscriber} not found")

        sub_channel, queue_name = self.info_to_start_consumer[subscriber]
        logger.info(f"Starting consumer for {subscriber} on {queue_name} via {sub_channel}")

        def consumer_thread():
            """
            Consumer thread
            :return:
            """
            sub_channel.basic_consume(queue=queue_name, on_message_callback=func, auto_ack=False)
            logger.info(f"Starting consumer for subscriber {subscriber}")
            sub_channel.start_consuming()

        thread = threading.Thread(target=consumer_thread)
        thread.start()

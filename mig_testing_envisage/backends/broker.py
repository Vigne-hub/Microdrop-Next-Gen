# broker.py
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost:5672/")
dramatiq.set_broker(rabbitmq_broker)
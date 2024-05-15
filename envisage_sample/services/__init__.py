import dramatiq
from traits.api import HasTraits, Str
from traits.has_traits import provides
from envisage_sample.Interfaces import IAnalysisService, ILoggingService

import json
import time

import dramatiq
import pika
from dramatiq.brokers.rabbitmq import RabbitmqBroker

# Set up the RabbitMQ broker
broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
dramatiq.set_broker(broker)


def send_response(result):
    broker.channel.basic_publish(
        exchange='',
        routing_key='response_backend_queue',  # Assume this queue is dedicated to receiving results
        body=str(result),
        properties=pika.BasicProperties(delivery_mode=2)  # Make messages persistent
    )
    print("__Response sent back to orchestrator")


##### Each of these services would need to have a model to define their payload which can be imported to use this service ####

@provides(IAnalysisService)
class AnalysisService(HasTraits):

    # task_name
    id = Str

    # define payload
    payload_model = Str('{"args_to_sum": []}')

    @staticmethod
    def process_task(task_info):
        print(f"Received task: {task_info}, processing in backend...")
        # Deserialize the task info from JSON
        task_data = json.loads(task_info)
        parameters = task_data.get('args_to_sum')
        time.sleep(2)
        result = sum(parameters)
        print("Analysis result:", result)
        return result


@provides(IAnalysisService)
class DramatiqAnalysisService(HasTraits):

    # task_name
    id = Str

    # define payload
    payload_model = Str('{"args_to_sum": []}')

    @dramatiq.actor
    def process_task(task_info):
        print(f"Received task: {task_info}, processing in backend...")
        # Deserialize the task info from JSON
        task_data = json.loads(task_info)
        parameters = task_data.get('args_to_sum')
        time.sleep(5)
        result = sum(parameters)
        print("Analysis result:", result)
        send_response(result)
        return result


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

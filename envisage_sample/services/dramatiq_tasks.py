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


@dramatiq.actor
def process_task(task_info):
    print(f"Received task: {task_info}, processing in backend...")
    # Deserialize the task info from JSON
    task_data = json.loads(task_info)
    parameters = task_data.get('args')
    time.sleep(5)
    result = sum(parameters)
    print("Analysis result:", result)
    send_response(result)
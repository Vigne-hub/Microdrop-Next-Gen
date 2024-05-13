import asyncio
import threading

import pika
from pydantic import BaseModel
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import backend


class TaskInfo(BaseModel):
    method: str
    parameters: dict


class Orchestrator:
    def __init__(self):
        self.backend_registry = {}
        self.GUI_registry = {}
        self.broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
        dramatiq.set_broker(self.broker)
        self.declare_publish_queues()
        self.consumer_thread = threading.Thread(target=self.start_consumers)
        self.consumer_thread.daemon = True
        self.consumer_thread.start()

    def register_GUI(self, GUI_id, GUI):
        self.GUI_registry[GUI_id] = GUI

    def register_backend(self, backend_id, backend):
        self.backend_registry[backend_id] = backend

    def start_consumers(self):
        connection = self.broker.connection
        channel = connection.channel()

        channel.queue_declare(queue='response_backend_queue')

        def callback(ch, method, properties, body):
            self.handle_responses(body)

        channel.basic_consume(queue='response_backend_queue', on_message_callback=callback, auto_ack=True)

        channel.queue_declare(queue='frontend_task_queue')

        def callback_frontend(ch, method, properties, body):
            task_info_json = body.decode('utf-8')
            process_task.send(task_info_json)

        channel.basic_consume(queue='frontend_task_queue', on_message_callback=callback_frontend, auto_ack=True)
        print("Starting to consume results...")
        print("Starting to consume tasks...")
        channel.start_consuming()

    def declare_publish_queues(self):
        connection = self.broker.connection
        channel = connection.channel()
        channel.queue_declare(queue='orc_response_queue')

    def handle_responses(self, response):
        print("Handling response...")
        print(response.decode('utf-8'))
        self.broker.channel.basic_publish(
            exchange='',
            routing_key='orc_response_queue',  # Assume this queue is dedicated to receiving results
            body=response.decode('utf-8'),
            properties=pika.BasicProperties(delivery_mode=2)  # Make messages persistent
        )


@dramatiq.actor
def process_task(task_info: str):
    print(f"Received task: {task_info}, processing in orchestrator...")
    #orchestrator.backend_registry[backend_id].process_task.send_with_options(args=task_info, delay=1000)
    backend.process_task.send(task_info)
    print(f"Task sent to backend via task_queue: {task_info}")

async def initialize():
    orchestrator = Orchestrator()
    await asyncio.Future()  # This will block forever unless a cancellation or exception occurs


if __name__ == "__main__":
    asyncio.run(initialize())

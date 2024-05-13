from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import json

app = FastAPI()

# Setup the RabbitMQ broker for Dramatiq
broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
dramatiq.set_broker(broker)


class TaskInfo(BaseModel):
    method: str
    parameters: dict


class Orchestrator:
    def __init__(self):
        self.backend_registry = {}
        self.start_consumer()

    def register_backend(self, backend_id, backend):
        self.backend_registry[backend_id] = backend

    def start_consumer(self):
        connection = broker.connection
        channel = connection.channel()
        channel.queue_declare(queue='response_queue')  # Ensure queue exists

        def callback(ch, method, properties, body):
            self.handle_responses(body)  # Process each message through handle_result actor

        channel.basic_consume(queue='response_queue', on_message_callback=callback, auto_ack=True)
        print("Starting to consume results...")
        channel.start_consuming()

    @dramatiq.actor
    def process_task(self, task_info: str, backend_id: str):
        print(f"Received task: {task_info}, processing in orchestrator...")
        self.backend_registry[backend_id].process_task.send_with_options(args=task_info, delay=1000)
        print(f"Task sent to backend via task_queue: {task_info}")

    @app.post("/dispatch_task/")
    async def dispatch_task(self, task_info: TaskInfo):
        # Serialize the task info to JSON string for Dramatiq
        task_info_json = task_info.model_dump_json()
        self.process_task.send(task_info_json)
        return {"status": "Task dispatched"}

    def handle_responses(self, response):
        pass


#channel.queue_declare(queue="task_queue", durable=True)
#channel.queue_declare(queue="response_queue", durable=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

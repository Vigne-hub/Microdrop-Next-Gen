from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import json

app = FastAPI()

# Setup the RabbitMQ broker for Dramatiq
broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
channel = broker.connection.channel()
dramatiq.set_broker(broker)

channel.queue_declare(queue="task_queue", durable=True)
channel.queue_declare(queue="response_queue", durable=True)


# Pydantic model for incoming task data
class TaskInfo(BaseModel):
    method: str
    parameters: dict


# Dramatiq actor to process the tasks
@dramatiq.actor
def process_task(task_info: str):
    print(f"Received task: {task_info}, processing in orchestrator...")
    channel.basic_publish(
        exchange="",
        routing_key="task_queue",
        body=task_info,
    )
    print(f"Task sent to backend via task_queue: {task_info}")


def receive_response():
    def callback(ch, method, properties, body):
        print("Received response from backend:", body.decode())
        channel.basic_publish(
            exchange="",
            routing_key="task_queue",
            body=body
        )

    channel.basic_consume(
        queue='response_queue',
        on_message_callback=callback,
        auto_ack=True
    )
    print("Waiting for responses from backend...")
    channel.start_consuming()


# Endpoint to dispatch tasks to the backend
@app.post("/dispatch_task/")
async def dispatch_task(task_info: TaskInfo):
    # Serialize the task info to JSON string for Dramatiq
    task_info_json = task_info.model_dump_json()
    process_task.send(task_info_json)
    return {"status": "Task dispatched"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

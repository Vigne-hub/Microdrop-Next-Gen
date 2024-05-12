# orchestrator.py
from fastapi import FastAPI, HTTPException
from dramatiq import actor
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import httpx
from pydantic import BaseModel

app = FastAPI()


class TaskPayload(BaseModel):
    backend_type: str
    task_type: str
    data: dict


# Setup RabbitMQ broker
broker = RabbitmqBroker(url="amqp://guest:guest@localhost")
dramatiq.set_broker(broker)

#example backends can be electrodes or dropbot etc...
backends = {
    "hardware": "http://localhost:8002/tasks",
    "database": "http://localhost:8003/tasks",
    "analytics": "http://localhost:8004/tasks",
}


@actor
def send_task(backend_type, task_type, data):
    url = backends.get(backend_type)
    if url:
        try:
            response = httpx.post(url, json={"task_type": task_type, "data": data})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as error:
            print(f"Failed to send task: {error}")
            # Implement retry or logging mechanism here
    else:
        print("No valid backend found")


@app.post("/orchestrate/")
async def orchestrate(task: TaskPayload):
    send_task.send(task.backend_type, task.task_type, task.data)
    return {"message": "Task orchestrated", "task_type": task.task_type, "backend": task.backend_type}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)

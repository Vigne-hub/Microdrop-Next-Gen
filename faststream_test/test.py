from faststream import FastStream
from faststream.rabbit import RabbitBroker
from pydantic import BaseModel, Field

# Define a Pydantic model for the messages
class Message(BaseModel):
    text: str = Field(..., description="Message text")

# Initialize the RabbitMQ Broker
broker = RabbitBroker("amqp://guest:guest@localhost:5672/")  # Adjust the connection string as needed
app = FastStream(broker)

# Define the subscriber and publisher
@broker.subscriber("in-queue")
@broker.publisher("out-queue")
async def process_message(message: Message) -> str:
    response = f"Processed message: {message.text}"
    return response

if __name__ == "__main__":
    app.run()

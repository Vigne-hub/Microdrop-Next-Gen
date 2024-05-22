# subscriber.py
import dramatiq
from broker import rabbitmq_broker

@dramatiq.actor(queue_name="notifications")
def consume_notification(message: str):
    print(f"Consuming notification: {message}")
    # Perform the action upon receiving the message
    # For example, logging, sending an email, etc.

if __name__ == "__main__":
    # To start the worker, run: dramatiq subscriber
    pass


# publisher.py
import dramatiq
from broker import rabbitmq_broker

@dramatiq.actor(queue_name="notifications")
def publish_notification(message: str):
    print(f"Publishing notification: {message}")
    # The actual work of publishing the message to the queue
    # This is handled by Dramatiq via the broker

if __name__ == "__main__":
    publish_notification.send("This is a test notification.")

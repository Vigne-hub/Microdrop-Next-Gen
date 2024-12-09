import subprocess
import time
import logging
from contextlib import contextmanager
import os

from dramatiq import get_broker, Worker

logger = logging.getLogger(__name__)


def is_redis_running():
    """Check if Redis is running by attempting to connect to it."""
    import redis
    try:
        client = redis.StrictRedis(host='localhost', port=6379)
        client.ping()
        return True
    except redis.exceptions.ConnectionError:
        return False


def start_redis_server(retries=5, wait=3):
    """Start the Redis server."""
    process = subprocess.Popen(["redis-server", f"{os.path.dirname(__file__)}{os.sep}redis.conf"])
    for _ in range(retries):  # Retry up to 5 times
        if is_redis_running():
            print("Redis server is running.")
            return process
        else:
            print("Waiting for Redis server to start...")
            time.sleep(wait)
    print("Failed to start Redis server.")
    process.terminate()
    return None


def stop_redis_server():
    import redis
    """Stop the Redis server."""
    try:
        client = redis.StrictRedis(host='localhost', port=6379)
        client.shutdown()
        print("Redis server stopped.")
    except redis.exceptions.ConnectionError as e:
        print(f"Failed to stop Redis server: {e}")


def remove_middleware_from_dramatiq_broker(middleware_name: str, broker: 'dramatiq.broker.Broker'):
    # Remove Prometheus middleware if it exists
    for el in broker.middleware:
        if el.__module__ == middleware_name:
            broker.middleware.remove(el)


def start_workers(**kwargs):
    """
    A startup routine for apps that make use of dramatiq.
    """
    BROKER = get_broker()

    worker = Worker(broker=BROKER, **kwargs)
    worker.start()


@contextmanager
def redis_server_context():
    """
    Context manager for apps that make use of a redis server
    """

    try:
        start_redis_server()

        yield  # This is where the main logic will execute within the context

    finally:
        # Shutdown routine
        stop_redis_server()


@contextmanager
def dramatiq_workers(**kwargs):
    """
    Context manager for apps that make use of dramatiq. They need the workers to exist.
    """
    remove_middleware_from_dramatiq_broker(middleware_name="dramatiq.middleware.prometheus", broker=get_broker())
    try:
        start_workers(**kwargs)

        yield  # This is where the main logic will execute within the context

    finally:
        # Shutdown routine
        get_broker().flush_all()


# Example usage
if __name__ == "__main__":
    from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
    import dramatiq


    def example_app_routine():
        # Given that I have a database
        database = {}

        @dramatiq.actor
        def put(message, topic):
            database[topic] = message

        test_topic = "test_topic"
        test_message = "test_message"
        # after declaring the actor, I add it to the message router and ascribe an topic to it that it will listen to.
        mra = MessageRouterActor()
        mra.message_router_data.add_subscriber_to_topic(topic=test_topic, subscribing_actor_name="put")
        # Now I publish a message to the message router actor to the test topic for triggering it.
        publish_message(test_message, test_topic, "message_router_actor")
        publish_message(message="test", topic="test")
        while True:
            if test_topic in database:
                print(f"Message: {database[test_topic]} successfully published on topic {test_topic}")
                exit(0)


    with redis_server_context():
        with dramatiq_workers():
            example_app_routine()

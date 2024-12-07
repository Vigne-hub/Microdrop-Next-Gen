import subprocess
import time
import sys
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


def init_broker_server(BROKER):
    try:
        from dramatiq.brokers.redis import RedisBroker
        # if we have a redis broker, start the server
        if isinstance(BROKER, RedisBroker):
            start_redis_server()
        else:
            logger.warning("BROKER must be a Redis broker.")

    except ImportError:
        logger.warning("Redis broker not available")

    except Exception as e:

        logger.error(f"No broker available. Exception:{e}")
        sys.exit(1)


def stop_broker_server(BROKER):
    try:
        from dramatiq.brokers.redis import RedisBroker

        # if we have a redis broker, stop the server
        if isinstance(BROKER, RedisBroker):
            stop_redis_server()
        else:
            logger.warning("BROKER must be a Redis broker.")

    except ImportError:
        logger.warning("Redis broker not available")

    except Exception as e:
        logger.error(f"No broker available. Exception {e}")
        sys.exit(1)


def startup_routine(**kwargs):
    """
    A startup routine for apps that make use of dramatiq.
    """
    BROKER = get_broker()
    # Startup routine
    BROKER.flush_all()
    # init_broker_server(BROKER)

    # Remove Prometheus middleware if it exists
    for el in BROKER.middleware:
        if el.__module__ == "dramatiq.middleware.prometheus":
            BROKER.middleware.remove(el)

    worker = Worker(broker=BROKER, **kwargs)
    worker.start()


def shutdown_routine():
    """
    A shutdown routine for apps that make use of dramatiq.
    """
    BROKER = get_broker()
    BROKER.flush_all()


@contextmanager
def redis_server_context():
    """
    Context manager for apps that make use of dramatiq.
    Ensures proper startup and shutdown routines.
    """

    start_redis_server()

    shutdown_routine()

    yield  # This is where the main logic will execute within the context

    shutdown_routine()
    # Shutdown routine
    stop_redis_server()


@contextmanager
def dramatiq_broker_context(**kwargs):
    """
    Context manager for apps that make use of dramatiq.
    Ensures proper startup and shutdown routines.
    """
    try:
        startup_routine(**kwargs)

        yield  # This is where the main logic will execute within the context

    finally:
        # Shutdown routine
        shutdown_routine()


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


    with dramatiq_broker_context():
        example_app_routine()

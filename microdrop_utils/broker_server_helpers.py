import subprocess
import time
import sys
import logging

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


def is_rabbitmq_running():
    """Check if RabbitMQ is running by attempting to connect to it using pika."""
    import pika
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        connection.close()
        return True
    except pika.exceptions.AMQPConnectionError:
        return False


def start_rabbitmq_server(retries=5, wait=3):
    """Start the RabbitMQ server."""
    process = subprocess.Popen(["rabbitmq-server"], shell=True)
    for _ in range(retries):  # Retry up to 5 times
        if is_rabbitmq_running():
            print("RabbitMQ server is running.")
            return process
        else:
            print("Waiting for RabbitMQ server to start...")
            time.sleep(wait)
    print("Failed to start RabbitMQ server.")
    process.terminate()
    return None


def stop_rabbitmq_server():
    """Stop the RabbitMQ server."""
    try:
        subprocess.run(["rabbitmqctl", "stop"], shell=True, check=True)
        print("RabbitMQ server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop RabbitMQ server: {e}")


def start_redis_server(retries=5, wait=3):
    """Start the Redis server."""
    process = subprocess.Popen(["redis-server"], shell=True)
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
    brokers = 2
    try:
        from dramatiq.brokers.redis import RedisBroker

        # if we have a redis broker, start the server
        if isinstance(BROKER, RedisBroker):
            redis_process = start_redis_server()
            if not redis_process:
                brokers -= 1
    except ImportError:
        brokers -= 1
        logger.warning("Redis broker not available")

    try:
        from dramatiq.brokers.rabbitmq import RabbitmqBroker

        # if we have a rabbitmq broker, start the server
        if isinstance(BROKER, RabbitmqBroker):
            rabbitmq_process = start_rabbitmq_server()
            if not rabbitmq_process:
                brokers -= 1
    except ImportError:
        brokers -= 1
        logger.warning("Rabbitmq broker not available")

    if brokers == 0:
        logger.error("No broker available. Exiting...")
        sys.exit(1)


def stop_broker_server(BROKER):
    brokers = 2

    try:
        from dramatiq.brokers.redis import RedisBroker

        # if we have a redis broker, stop the server
        if isinstance(BROKER, RedisBroker):
            stop_redis_server()
    except ImportError:
        logger.warning("Redis broker not available")
        brokers -= 1

    try:
        from dramatiq.brokers.rabbitmq import RabbitmqBroker

        # if we have a rabbitmq broker, stop the server
        if isinstance(BROKER, RabbitmqBroker):
            stop_rabbitmq_server()
    except ImportError:
        logger.warning("Rabbitmq broker not available")
        brokers -= 1

    if brokers == 0:
        logger.error("No broker available. Exiting...")
        sys.exit(1)


# Example usage
if __name__ == "__main__":
    import dramatiq

    try:
        init_broker_server(dramatiq.get_broker())
        # Run your main application logic here
    finally:
        stop_broker_server(dramatiq.get_broker())

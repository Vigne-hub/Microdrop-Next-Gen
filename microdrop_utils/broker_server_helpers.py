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


# Example usage
if __name__ == "__main__":
    import dramatiq

    try:
        init_broker_server(dramatiq.get_broker())
        # Run your main application logic here
    finally:

        stop_broker_server(dramatiq.get_broker())

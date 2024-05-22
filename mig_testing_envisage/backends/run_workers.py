# run_workers.py
import dramatiq
from dramatiq import Worker
from broker import rabbitmq_broker  # Ensure broker is imported to set up correctly
import sub  # Ensure subscriber is imported to register the actor

def run_workers():
    worker = Worker(rabbitmq_broker)
    worker.start()
    return worker

if __name__ == "__main__":
    worker = run_workers()
    try:
        # Keep the main thread alive while workers run
        while True:
            pass
    except KeyboardInterrupt:
        # Gracefully stop the worker on interrupt
        worker.stop()
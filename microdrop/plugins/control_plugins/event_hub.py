import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from envisage.core_plugin import CorePlugin
from traits.api import List

from ...utils.logger import initialize_logger

logger = initialize_logger(__name__)

# Setup RabbitMQ broker for Dramatiq
rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class EventHubPlugin(CorePlugin):
    id = 'app.event_hub'
    name = 'Event Hub Plugin'
    service_offers = List(contributes_to='envisage.service_offers')
    process_task_actor = None

    def start(self):
        super().start()
        logger.info("Event Hub Plugin started")
        self._start_worker()
        self._start_actor()

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()

    def _start_actor(self):
        @dramatiq.actor(queue_name='eventhub_actions')
        def process_task(task):
            interface_name = task.get("interface")
            service_name = task.get("service")
            task_name = task.get("task_name")
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})
            logger.info(f"Processing task: {task}")

            try:
                service = self.application.get_service(f"microdrop.interfaces.{interface_name}.{service_name}")
            except AttributeError as e:
                logger.error(f"Error while getting service: {e}")
                return

            method = getattr(service, task_name)
            if callable(method):
                result = method(*args, **kwargs)
                print(f"Task {task_name} completed with result: {result}")
                logger.info(f"Task {task_name} completed with result: {result}")
                return result
            else:
                logger.error(f"Task '{task_name}' on service '{service_name}' is not callable.")

        self.process_task_actor = process_task
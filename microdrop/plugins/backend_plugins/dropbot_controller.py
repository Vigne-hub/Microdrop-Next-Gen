from envisage.api import ServiceOffer
from envisage.plugin import Plugin
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker

from ...interfaces.i_dropbot_controller_service import IDropbotControllerService
from ...utils.logger import initialize_logger

# Initialize logger
logger = initialize_logger(__name__)

# Setup RabbitMQ broker for Dramatiq
rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class DropbotControllerPlugin(Plugin):
    id = 'app.dropbot_controller'
    name = 'Dropbot Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        self._start_worker()
        self._start_actor()

    def _register_services(self):
        self.dropbot_service = self._create_service()
        self.application.register_service(IDropbotControllerService, self.dropbot_service)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IDropbotControllerService, factory=self._create_service)
        ]

    def _create_service(self):
        from microdrop.services.dropbot_services import DropbotService
        return DropbotService(self.application)

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()

    def _start_actor(self):
        @staticmethod
        @dramatiq.actor(queue_name='dropbot_actions')
        def process_task(task):
            method_name = task.get("task_name")
            task_args = task.get("args")
            task_kwargs = task.get("kwargs")
            logger.info(f"Processing task: {task}")

            # Map task names to DropbotController methods
            task_map = {
                "poll_voltage": lambda: self.dropbot_service.poll_voltage(),
                "set_voltage": lambda: self.dropbot_service.set_voltage(*task_args, **task_kwargs),
                "set_frequency": lambda: self.dropbot_service.set_frequency(*task_args, **task_kwargs),
                "set_hv": lambda: self.dropbot_service.set_hv(*task_args, **task_kwargs),
                "get_channels": lambda: self.dropbot_service.get_channels(),
                "set_channels": lambda: self.dropbot_service.set_channels(*task_args, **task_kwargs),
                "set_channel_single": lambda: self.dropbot_service.set_channel_single(*task_args, **task_kwargs),
                "droplet_search": lambda: self.dropbot_service.droplet_search(*task_args, **task_kwargs),
            }

            if method_name in task_map:
                result = task_map[method_name]()
                logger.info(f"Task {method_name} completed with result: {result}")
                return result
            else:
                logger.error(f"Unknown task name: {method_name}")
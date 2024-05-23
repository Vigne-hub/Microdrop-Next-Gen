from envisage.api import Plugin, ServiceOffer
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import logging

from refrac_qt_microdrop.helpers.dropbot_controller_helper import DropbotController
from refrac_qt_microdrop.interfaces.dropbot_interface import IDropbotControllerService

# Initialize logger
logger = logging.getLogger(__name__)

# Setup RabbitMQ broker for Dramatiq
rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class DropbotControllerPlugin(Plugin):
    id = 'refrac_qt_microdrop.dropbot_controller'
    name = 'Dropbot Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        logger.info("DropbotController Plugin started")
        self._start_worker()

    def _register_services(self):
        dropbot_service = self._create_service()
        self.application.register_service(IDropbotControllerService, dropbot_service)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IDropbotControllerService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        from refrac_qt_microdrop.services.dropbot_services import DropbotService
        return DropbotService()

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()


class DropbotActor:

    @staticmethod
    @dramatiq.actor(queue_name='dropbot_actions')
    def process_task(task):
        print(f"Processing task: {task}")
        task_name = task.get("name")
        print(f"Task name: {task_name}")
        task_args = task.get("args")
        print(f"Task args: {task_args}")
        task_kwargs = task.get("kwargs")
        print(f"Task kwargs: {task_kwargs}")
        logger.info(f"Processing task: {task}")

        # Map task names to DropbotController methods
        task_map = {
            "poll_voltage": lambda: DropbotController().poll_voltage(),
            "set_voltage": lambda: DropbotController().set_voltage(*task_args, **task_kwargs),
            "set_frequency": lambda: DropbotController().set_frequency(*task_args, **task_kwargs),
            "set_hv": lambda: DropbotController().set_hv(*task_args, **task_kwargs),
            "get_channels": lambda: DropbotController().get_channels(),
            "set_channels": lambda: DropbotController().set_channels(*task_args, **task_kwargs),
            "set_channel_single": lambda: DropbotController().set_channel_single(*task_args, **task_kwargs),
            "droplet_search": lambda: DropbotController().droplet_search(*task_args, **task_kwargs),
        }

        if task_name in task_map:
            result = task_map[task_name]()
            print(f"Task {task_name} completed with result: {result}")
            logger.info(f"Task {task_name} completed with result: {result}")
            return result
        else:
            logger.error(f"Unknown task name: {task_name}")

from envisage.api import ServiceOffer
from envisage.core_plugin import CorePlugin
from envisage.plugin import Plugin
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import logging

from MicroDropNG.backend_logic.dropbot_controller import DropbotController
from MicroDropNG.interfaces.dropbot_interface import IDropbotControllerService

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
    id = 'app.dropbot_controller'
    name = 'Dropbot Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        logger.info("DropbotController Plugin started")
        self._start_worker()
        init_global_dropbot(self.application)

    def _register_services(self):
        dropbot_service = self._create_service()
        self.application.register_service(IDropbotControllerService, dropbot_service)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IDropbotControllerService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        from MicroDropNG.services.dropbot_services import DropbotService
        return DropbotService()

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()


global dropbot


def init_global_dropbot(app):
    global dropbot
    dropbot = DropbotController(app)


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

        if dropbot is None:
            logger.error("DropbotController instance is not initialized.")
            return

        # Map task names to DropbotController methods
        task_map = {
            "poll_voltage": lambda: dropbot.poll_voltage(),
            "set_voltage": lambda: dropbot.set_voltage(*task_args, **task_kwargs),
            "set_frequency": lambda: dropbot.set_frequency(*task_args, **task_kwargs),
            "set_hv": lambda: dropbot.set_hv(*task_args, **task_kwargs),
            "get_channels": lambda: dropbot.get_channels(),
            "set_channels": lambda: dropbot.set_channels(*task_args, **task_kwargs),
            "set_channel_single": lambda: dropbot.set_channel_single(*task_args, **task_kwargs),
            "droplet_search": lambda: dropbot.droplet_search(*task_args, **task_kwargs),
        }

        if task_name in task_map:
            result = task_map[task_name]()
            print(f"Task {task_name} completed with result: {result}")
            logger.info(f"Task {task_name} completed with result: {result}")
            return result
        else:
            logger.error(f"Unknown task name: {task_name}")

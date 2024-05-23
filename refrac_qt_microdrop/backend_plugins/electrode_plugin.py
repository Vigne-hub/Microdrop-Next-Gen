# plugins/electrode_plugin.py
from envisage.api import Plugin, ServiceOffer
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import logging

from refrac_qt_microdrop.interfaces.electrode_interface import IElectrodeControllerService
from refrac_qt_microdrop.services.electrode_services import ElectrodeService

# Initialize logger
logger = logging.getLogger(__name__)

# Setup RabbitMQ broker for Dramatiq
rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)
# Remove Prometheus middleware if it exists
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)

class ElectrodeControllerPlugin(Plugin):
    id = 'refrac_qt_microdrop.electrode_controller'
    name = 'Electrode Controller Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        logger.info("ElectrodeController Plugin started")
        self._start_worker()

    def _register_services(self):
        electrode_service = self._create_service()
        self.application.register_service(IElectrodeControllerService, electrode_service)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IElectrodeControllerService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        return ElectrodeService()

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start)
        worker_thread.daemon = True
        worker_thread.start()

class ElectrodeActor:

    @staticmethod
    @dramatiq.actor(queue_name='electrode_actions')
    def process_task(task):
        from refrac_qt_microdrop.helpers.electrode_helper import Electrode, Electrodes
        electrodes = Electrodes()

        print(f"Processing task: {task}")
        task_name = task.get("name")
        print(f"Task name: {task_name}")
        task_args = task.get("args")
        print(f"Task args: {task_args}")
        task_kwargs = task.get("kwargs")
        print(f"Task kwargs: {task_kwargs}")
        logger.info(f"Processing task: {task}")

        # Map task names to Electrode methods
        task_map = {
            "toggle_state": lambda: electrodes[task_args[0]].toggle_state(),
            "set_state": lambda: electrodes[task_args[0]].set_state(*task_args[1:], **task_kwargs),
            "get_state": lambda: electrodes[task_args[0]].get_state(),
            "set_metastate": lambda: electrodes[task_args[0]].set_metastate(*task_args[1:], **task_kwargs),
            "get_metastate": lambda: electrodes[task_args[0]].get_metastate(),
        }

        if task_name in task_map:
            result = task_map[task_name]()
            print(f"Task {task_name} completed with result: {result}")
            logger.info(f"Task {task_name} completed with result: {result}")
            return result
        else:
            logger.error(f"Unknown task name: {task_name}")

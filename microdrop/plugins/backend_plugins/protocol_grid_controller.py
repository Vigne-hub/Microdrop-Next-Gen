from envisage.api import Plugin, ServiceOffer
from traits.api import List
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import threading

from ...interfaces.i_protocol_grid_controller_service import IPGSService
from microdrop_utils._logger import get_logger

logger = get_logger(__name__)

rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)

for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class ProtocolGridBackendPlugin(Plugin):
    id = 'app.protocol_grid_backend'
    name = 'Protocol Grid Backend Plugin'
    service_offers = List(contributes_to='envisage.service_offers')
    process_task_actor = None

    def start(self):
        super().start()
        self._register_services()
        logger.info("ProtocolGrid Backend Plugin started")
        self._start_worker()
        self._start_actor()

    def _register_services(self):
        protocol_grid_service = self._create_service()
        self.application.register_service(IPGSService, protocol_grid_service)
        logger.info("Registered ProtocolGridStructure service")

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IPGSService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        return IPGSService()

    def _start_worker(self):
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start)
        worker_thread.daemon = True
        worker_thread.start()
        logger.info("Started worker thread")

    def _start_actor(self):
        @dramatiq.actor(queue_name='protocol_grid_actions')
        def process_task(task):
            protocol_grid_service = self.application.get_service(IPGSService)
            if protocol_grid_service:
                task_name = task.get("method_name")
                task_args = task.get("args")
                task_kwargs = task.get("kwargs")
                logger.info(f"Processing task: {task}")

                task_map = {
                    "add_step": lambda: protocol_grid_service.add_step(*task_args, **task_kwargs),
                    "add_electrode_to_step": lambda: protocol_grid_service.add_electrode_to_step(*task_args,
                                                                                                 **task_kwargs),
                    "remove_electrode_from_step": lambda: protocol_grid_service.remove_electrode_from_step(*task_args,
                                                                                                           **task_kwargs),
                    "get_electrodes_on_for_step": lambda: protocol_grid_service.get_electrodes_on_for_step(*task_args,
                                                                                                           **task_kwargs),
                    "save_protocol": lambda: protocol_grid_service.save_protocol(*task_args, **task_kwargs),
                    "load_protocol": lambda: protocol_grid_service.load_protocol(*task_args, **task_kwargs),
                    "save_to_file": lambda: protocol_grid_service.save_to_file(*task_args, **task_kwargs)
                }

                if task_name in task_map:
                    result = task_map[task_name]()
                    logger.info(f"Task {task_name} completed with result: {result}")
                    return result
                else:
                    logger.error(f"Unknown task name: {task_name}")
            else:
                logger.error("PGS service not found!")

        self.process_task_actor = process_task  # Store the actor for reference
        logger.info("Started actor")



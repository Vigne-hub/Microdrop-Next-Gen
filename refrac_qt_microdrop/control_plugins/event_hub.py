# plugins/event_hub_plugin.py
import importlib
import logging

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from envisage.api import Plugin
from envisage.service_offer import ServiceOffer
from traits.api import List

from refrac_qt_microdrop.interfaces.event_hub_interface import IEventHubService

logger = logging.getLogger(__name__)
# Setup RabbitMQ broker for Dramatiq
rabbitmq_broker = RabbitmqBroker(url="amqp://guest:guest@localhost/")
dramatiq.set_broker(rabbitmq_broker)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class EventHubPlugin(Plugin):
    id = 'refrac_qt_microdrop.event_hub'
    name = 'Event Hub Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        logger.info("Event Hub Plugin started")
        self._start_worker()
        global application
        application = self.application

    def _register_services(self):
        event_hub_services = self._create_service()
        self.application.register_service(IEventHubService, event_hub_services)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IEventHubService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        from refrac_qt_microdrop.services.event_hub_services import EventHubService
        return EventHubService()

    def _start_worker(self):
        import threading
        from dramatiq import Worker

        worker = Worker(broker=rabbitmq_broker)
        worker_thread = threading.Thread(target=worker.start())
        worker_thread.daemon = True
        worker_thread.start()


class EventHubActor:

    list_of_protocols = {}
    imported_modules = []

    @staticmethod
    @dramatiq.actor(queue_name='eventhub_actions')
    def process_task(task):
        print(f"Processing task: {task}")
        service_name = task.get("service_name")
        task_name = task.get("task_name")
        args = task.get("args", [])
        kwargs = task.get("kwargs", {})
        logger.info(f"Processing task: {task}")

        if not application:
            logger.error("No Envisage application instance found.")
            return

        interface_module, protocol_name = service_name.split('.')

        if interface_module not in EventHubActor.list_of_protocols:
            EventHubActor.list_of_protocols[interface_module] = protocol_name
            imported_module = importlib.import_module(f"refrac_qt_microdrop.interfaces.{interface_module}")
            EventHubActor.imported_modules.append(imported_module)

        try:
            service = application.get_service(getattr(importlib.import_module(f"refrac_qt_microdrop.interfaces.{interface_module}"), protocol_name))
        except AttributeError as e:
            logger.error(f"Error while getting service: {e}")
            return

        if not hasattr(service, task_name):
            logger.error(f"Service '{service_name}' does not have task '{task_name}'.")
            return

        method = getattr(service, task_name)
        if callable(method):
            result = method(*args, **kwargs)
            print(f"Task {task_name} completed with result: {result}")
            logger.info(f"Task {task_name} completed with result: {result}")
            return result
        else:
            logger.error(f"Task '{task_name}' on service '{service_name}' is not callable.")
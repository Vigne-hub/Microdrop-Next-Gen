# plugins/event_hub_plugin.py
import logging

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from envisage.api import Plugin
from envisage.service_offer import ServiceOffer
from traits.api import List
from refrac_qt_microdrop.interfaces.dropbot_interface import IDropbotControllerService
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
        logger.info("DropbotController Plugin started")
        self._start_worker()

    def _register_services(self):
        event_hub_services = self._create_service()
        self.application.register_service(IDropbotControllerService, dropbot_service)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=EventHubPlugin, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        dropbot_service = self.application.get_service(IDropbotControllerService)
        return EventHubPlugin(dropbot_service)

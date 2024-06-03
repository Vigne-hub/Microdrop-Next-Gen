import logging

from envisage.api import Plugin, ServiceOffer
from traits.api import List

from MicrodropNG.interfaces.pub_sub_manager_interface import IPubSubManagerService
from MicrodropNG.services.pub_sub_manager_services import PubSubManager

# Initialize logger
logger = logging.getLogger(__name__)


class PubSubManagerPlugin(Plugin):
    id = 'my_app.pubsub_manager'
    name = 'PubSub Manager Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        logger.info("PubSubManager Plugin started")

    def _register_services(self):
        pubsub_service = self._create_service()
        self.application.register_service(IPubSubManagerService, pubsub_service)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IPubSubManagerService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        return PubSubManager()

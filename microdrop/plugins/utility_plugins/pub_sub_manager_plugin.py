import logging

from envisage.api import ServiceOffer
from envisage.core_plugin import CorePlugin
from traits.api import List

from microdrop.interfaces.i_pub_sub_manager_service import IPubSubManagerService
from microdrop.services.pub_sub_manager_services import PubSubManager

# Initialize logger
logger = logging.getLogger(__name__)


class PubSubManagerPlugin(CorePlugin):
    id = 'app.pubsub_manager'
    name = 'PubSub Manager Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=IPubSubManagerService, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        return PubSubManager()
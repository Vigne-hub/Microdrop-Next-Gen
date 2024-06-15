from envisage.api import ServiceOffer
from envisage.core_plugin import CorePlugin
from traits.api import List

from ...interfaces.i_pub_sub_manager_service import IPubSubManagerService
from ...services.pub_sub_manager_services import PubSubManager
from ...utils.logger import initialize_logger

# Initialize logger
logger = initialize_logger(__name__)


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
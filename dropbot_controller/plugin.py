from envisage.api import ServiceOffer
from envisage.ids import SERVICE_OFFERS
from envisage.plugin import Plugin
from traits.api import List, observe
import dramatiq

from dropbot_controller.dropbot_controller_base import DropbotControllerBase
from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService
from dropbot_controller.public_constants import ACTOR_TOPIC_DICT
from dropbot_controller.services.dropbot_monitor_mixin_service import DropbotMonitorMixinService
from message_router.public_constants import ACTOR_TOPIC_ROUTES
from microdrop_utils._logger import get_logger

# Initialize logger
logger = get_logger(__name__)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class DropbotControllerPlugin(Plugin):
    id = 'dropbot_controller'
    name = 'Dropbot Controller'

    # this plugin contributes some service offers
    service_offers = List(contributes_to=SERVICE_OFFERS)

    # This plugin contributes some actors that can be called using certain routing keys.
    actor_topic_routing = List([ACTOR_TOPIC_DICT], contributes_to=ACTOR_TOPIC_ROUTES)

    def _service_offers_default(self):
        """Return the service offers."""
        return [
            ServiceOffer(protocol=IDropbotControlMixinService, factory=self._create_service),
        ]

    def _create_service(self, *args, **kwargs):
        """Create an analysis service."""
        return DropbotMonitorMixinService

    def start(self):
        """ Initialize the dropbot on plugin start """

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

        # Lookup the dropbot controller related mixin class services and add to base class.
        services = self.application.get_services(IDropbotControlMixinService) + [DropbotControllerBase]
        logger.info(f"The following dropbot services are going to be initialized: {services} ")

        # Combine the classes into a new dropbot controller class
        DropbotController = type('DropbotController', tuple(services), {})

        self.dropbot_controller = DropbotController()
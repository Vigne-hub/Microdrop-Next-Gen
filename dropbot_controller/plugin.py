from envisage.api import ServiceOffer
from envisage.ids import SERVICE_OFFERS
from envisage.plugin import Plugin
from traits.api import List

from dropbot_controller.dropbot_controller_base import DropbotControllerBase
from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService
from dropbot_controller.consts import ACTOR_TOPIC_DICT
from dropbot_controller.services.dropbot_monitor_mixin_service import DropbotMonitorMixinService
from message_router.public_constants import ACTOR_TOPIC_ROUTES
from microdrop_utils._logger import get_logger

from .consts import PKG

# Initialize logger
logger = get_logger(__name__)


class DropbotControllerPlugin(Plugin):
    id = PKG + '.plugin'
    name = 'Dropbot Controller Plugin'

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
        """Returns a dropbot monitor mixin service with core functionality."""
        return DropbotMonitorMixinService

    def start(self):
        """ Initialize the dropbot on plugin start """

        # Note that we always offer the service via its name, but look it up via the actual protocol.
        from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

        # Lookup the dropbot controller related mixin class services and add to base class.
        services = self.application.get_services(IDropbotControlMixinService) + [DropbotControllerBase]
        logger.debug(f"The following dropbot services are going to be initialized: {services} ")

        self.dropbot_controller = type('DropbotController', tuple(services), {})()

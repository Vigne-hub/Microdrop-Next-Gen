from envisage.api import ServiceOffer
from envisage.ids import SERVICE_OFFERS
from envisage.plugin import Plugin
from traits.api import List, observe
import dramatiq

from dropbot_controller.dropbot_controller_base import DropbotControllerBase
from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService
from dropbot_controller.services.dropbot_monitor_mixin_service import DropbotMonitorMixinService
from microdrop_utils._logger import get_logger

# Initialize logger
logger = get_logger(__name__)
# remove prometheus metrics for now
for el in dramatiq.get_broker().middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        dramatiq.get_broker().middleware.remove(el)


class DropbotControllerPlugin(Plugin):
    id = 'app.dropbot_controller'
    name = 'Dropbot Plugin'

    service_offers = List(contributes_to=SERVICE_OFFERS)

    def _service_offers_default(self):
        """Return the service offers."""
        return [
            ServiceOffer(protocol=IDropbotControlMixinService, factory=self._create_service),
        ]

    def _create_service(self, *args, **kwargs):
        """Create an analysis service."""

        # TODO: while this creation happens, automatically we get the kwargs as the properties defined in the service
        # offer. We have to exploit this somehow. Its a useful behavious potentially
        return DropbotMonitorMixinService

    @observe('application:started')
    def _intitalize_dropbot(self, event):
        """ Print the 'Message of the Day' to stdout! """

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

        # Lookup the dropbot controller related mixin class services and add to base class.
        services = self.application.get_services(IDropbotControlMixinService) + [DropbotControllerBase]
        logger.info(f"The following dropbot services are going to be initialized: {services} ")

        # Combine the classes into a new dropbot controller class
        DropbotController = type('DropbotController', tuple(services), {})

        dropbot_controller = DropbotController()
        return

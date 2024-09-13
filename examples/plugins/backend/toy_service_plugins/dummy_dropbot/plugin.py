from envisage.api import Plugin, SERVICE_OFFERS
from envisage.service_offer import ServiceOffer
from traits.trait_types import List

from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService
from .services.dummy_dropbot_control_service import DropbotDummyMixinService


class DummyDropbotServicePlugin(Plugin):
    id = 'app.analysis.plugin'
    service_offers = List(contributes_to=SERVICE_OFFERS)

    def _service_offers_default(self):
        """Return the service offers."""
        return [
            ServiceOffer(protocol=IDropbotControlMixinService, factory=self._create_service),
        ]

    def _create_service(self, *args, **kwargs):
        """Create an analysis service."""
        return DropbotDummyMixinService

from envisage.api import Plugin, SERVICE_OFFERS
from envisage.service_offer import ServiceOffer
from traits.trait_types import List

from .interfaces.i_logging_service import ILoggingService
from .services.logging_service import LoggingService


class LoggingPlugin(Plugin):
    id = 'app.logging.plugin'
    service_offers = List(contributes_to=SERVICE_OFFERS)

    def _service_offers_default(self):
        return [ServiceOffer(protocol=ILoggingService, factory=self._create_service)]

    def _create_service(self):
        return LoggingService()

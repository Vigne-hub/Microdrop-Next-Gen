from envisage.core_plugin import CorePlugin
from envisage.service_offer import ServiceOffer
from traits.trait_types import List

from envisage_sample.interfaces.i_logging_service import ILoggingService
from envisage_sample.services.logging_service import LoggingService


class LoggingPlugin(CorePlugin):
    id = 'app.logging.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        return [ServiceOffer(protocol=ILoggingService, factory=self._create_service)]

    def _create_service(self):
        return LoggingService()

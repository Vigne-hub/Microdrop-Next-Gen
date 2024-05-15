from envisage.api import Plugin, ServiceOffer
from traits.api import List

class LoggingPlugin(Plugin):
    id = 'app.logging.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        return [ServiceOffer(protocol='services.logging_service.LoggingService', factory=self._create_service)]

    def _create_service(self):
        from envisage_sample.services.logging_service import LoggingService
        return LoggingService()

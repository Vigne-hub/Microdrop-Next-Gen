from envisage.api import Plugin, ServiceOffer
from traits.api import List
from envisage_sample.services import IAnalysisService, ILoggingService
from envisage_sample.services import AnalysisService, LoggingService


class BackendPlugin(Plugin):
    id = 'app.backend.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        """Start the plugin."""

        # Register all service offers.
        #
        # These services are unregistered by the default plugin activation
        # strategy (due to the fact that we store the service ids in this
        # specific trait!).
        self._service_ids = self._register_service_offers(self.service_offers)

    def _service_offers_default(self):
        pass

    def _create_service(self, *args, **kwargs):
        pass

    def _register_service_offers(self, service_offers):
        """Register a list of service offers."""

        return list(map(self._register_service_offer, service_offers))

    def _register_service_offer(self, service_offer):
        """Register a service offer."""

        service_id = self.application.register_service(
            protocol=service_offer.protocol,
            obj=service_offer.factory,
            properties=service_offer.properties,
        )

        return service_id


class AnalysisPlugin(BackendPlugin):
    id = 'app.analysis.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        """Return the service offers."""
        return [
            ServiceOffer(protocol=IAnalysisService, factory=self._create_service, properties={"operation": "add"}),
        ]

    def _create_service(self, *args, **kwargs):
        """Create an analysis service."""

        # TODO: while this cretion happens, automatically we get the kwargs as the properties defined in the service
        # offer. We have to exploit this somehow. Its a useful behavious potentially
        return AnalysisService(payload_model='{"args": []}')


class LoggingPlugin(BackendPlugin):
    id = 'app.logging.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        return [ServiceOffer(protocol=ILoggingService, factory=self._create_service)]

    def _create_service(self):
        return LoggingService()

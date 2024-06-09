from envisage.core_plugin import CorePlugin
from envisage.service_offer import ServiceOffer
from traits.trait_types import List

from .interfaces.i_analysis_service import IAnalysisService
from .services.analysis_service import AnalysisService
from .services.dramatiq_analysis_service import DramatiqAnalysisService


class AnalysisPlugin(CorePlugin):
    id = 'app.analysis.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        """Return the service offers."""
        return [
            ServiceOffer(protocol=IAnalysisService, factory=self._create_service, properties={"type": "regular"}),
            ServiceOffer(protocol=IAnalysisService, factory=self._create_service_dramatiq,

                         properties={
                             "type": "dramatiq",
                             "id": "dramatiq_analysis_service",

                         })
        ]

    def _create_service(self, *args, **kwargs):
        """Create an analysis service."""

        # TODO: while this creation happens, automatically we get the kwargs as the properties defined in the service
        # offer. We have to exploit this somehow. Its a useful behavious potentially
        return AnalysisService(id="analysis_service", payload_model='')

    def _create_service_dramatiq(self, id, *args, **kwargs):
        """Create an analysis service."""

        return DramatiqAnalysisService(id=id)

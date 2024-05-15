from envisage.api import Plugin, ServiceOffer
from traits.api import List

class AnalysisPlugin(Plugin):
    id = 'app.analysis.plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def _service_offers_default(self):
        return [ServiceOffer(protocol='services.analysis_service.AnalysisService', factory=self._create_service)]

    def _create_service(self):
        from envisage_sample.services.analysis_service import AnalysisService
        return AnalysisService()

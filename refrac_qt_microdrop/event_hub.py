# plugins/event_hub_plugin.py
from envisage.api import Plugin
from envisage.service_offer import ServiceOffer
from traits.api import List
from refrac_qt_microdrop.interfaces.dropbot_interface import IDropbotControllerService
from refrac_qt_microdrop.interfaces.electrode_interface import IElectrodeControllerService

class EventHubPlugin(Plugin):
    id = 'refrac_qt_microdrop.event_hub'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        dropbot_service = self.application.get_service(IDropbotControllerService)
        electrode_service = self.application.get_service(IElectrodeControllerService)
        event_hub = EventHubPlugin(dropbot_service, electrode_service)
        self.application.register_service(EventHubPlugin, event_hub)

    def _service_offers_default(self):
        return [
            ServiceOffer(protocol=EventHubPlugin, factory=self._create_service)
        ]

    def _create_service(self, *args, **kwargs):
        dropbot_service = self.application.get_service(IDropbotControllerService)
        electrode_service = self.application.get_service(IElectrodeControllerService)
        return EventHub(dropbot_service, electrode_service)

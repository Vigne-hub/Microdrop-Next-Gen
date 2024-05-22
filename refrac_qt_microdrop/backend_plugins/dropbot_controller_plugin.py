from envisage.api import Plugin, ServiceOffer
from traits.api import List
from refrac_qt_microdrop.services import VoltageService, OutputService, ChannelService
from refrac_qt_microdrop.interfaces import IVoltageService, IOutputService, IChannelService

class DropbotPlugin(Plugin):
    id = 'app.dropbot.plugin'
    name = 'Dropbot Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()

    def _register_services(self):
        voltage_service = self._create_voltage_service()
        output_service = self._create_output_service()
        channel_service = self._create_channel_service()
        self.application.register_service(IVoltageService, voltage_service)
        self.application.register_service(IOutputService, output_service)
        self.application.register_service(IChannelService, channel_service)

    def _service_offers_default(self):
        return []

    def _create_voltage_service(self):
        print("Creating VoltageService")
        return VoltageService()

    def _create_output_service(self):
        print("Creating OutputService")
        return OutputService()

    def _create_channel_service(self):
        print("Creating ChannelService")
        return ChannelService()

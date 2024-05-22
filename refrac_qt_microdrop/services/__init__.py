from traits.api import HasTraits, provides
from refrac_qt_microdrop.interfaces import IDropbotControllerService
from refrac_qt_microdrop.backend_plugins.dropbot_controller import DropbotControllerLogic

@provides(IDropbotControllerService)
class DropbotService(HasTraits):
    def __init__(self):
        self.controller = DropbotControllerLogic()

    def init_dropbot_proxy(self):
        return self.controller.init_dropbot_proxy()

    def poll_voltage(self):
        return self.controller.poll_voltage.send()

    def set_voltage(self, voltage: int):
        return self.controller.set_voltage.send_with_options(voltage)

    def set_frequency(self, frequency: int):
        return self.controller.set_frequency.send(frequency)

    def set_hv(self, on: bool):
        return self.controller.set_hv.send(on)

    def get_channels(self):
        return self.controller.get_channels.send()

    def set_channels(self, channels):
        return self.controller.set_channels.send(channels)

    def set_channel_single(self, channel: int, state: bool):
        return self.controller.set_channel_single.send(channel, state)

    def droplet_search(self, threshold: float = 0):
        return self.controller.droplet_search.send(threshold)

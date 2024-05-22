from traits.api import Interface

class IDropbotControllerService(Interface):
    def init_dropbot_proxy(self):
        pass

    def poll_voltage(self):
        pass

    def set_voltage(self, voltage: int):
        pass

    def set_frequency(self, frequency: int):
        pass

    def set_hv(self, on: bool):
        pass

    def get_channels(self):
        pass

    def set_channels(self, channels):
        pass

    def set_channel_single(self, channel: int, state: bool):
        pass

    def droplet_search(self, threshold: float = 0):
        pass

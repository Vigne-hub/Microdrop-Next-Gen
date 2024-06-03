from traits.api import Interface


class IEventHubService(Interface):

    def set_voltage_button_clicked(self, voltage, callback):
        pass

    def set_frequency_button_clicked(self, frequency, callback):
        pass

    def set_hv_button_clicked(self, on: bool):
        pass

    def get_channels_button_clicked(self):
        pass

    def set_channels_button_clicked(self, channels):
        pass

    def set_channel_single_button_clicked(self, channel: int, state: bool):
        pass

    def droplet_search_button_clicked(self, threshold: float = 0):
        pass

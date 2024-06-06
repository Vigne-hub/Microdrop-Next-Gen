from traits.api import Interface


class IDropbotControllerService(Interface):

    def poll_voltage(self):
        """ Poll the voltage from the Dropbot """

    def set_voltage(self, voltage: int):
        """ Set the voltage of the Dropbot """

    def set_frequency(self, frequency: int):
        """ Set the frequency of the Dropbot """

    def set_hv(self, on: bool):
        """ Enable or disable the high voltage output of the Dropbot """

    def get_channels(self):
        """ Get the current state of all channels from the Dropbot """

    def set_channels(self, channels):
        """ Set the state of all channels on the Dropbot """

    def set_channel_single(self, channel: int, state: bool):
        """ Set the state of a single channel on the Dropbot """

    def droplet_search(self, threshold: float = 0):
        """ Search for droplets on the Dropbot """

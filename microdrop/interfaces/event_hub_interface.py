from traits.api import Interface


class IEventHubService(Interface):

    def set_voltage_button_clicked(self, voltage, callback):
        """ Set the voltage of the Dropbot Button clicked response """

    def set_frequency_button_clicked(self, frequency, callback):
        """ Set the frequency of the Dropbot Button clicked response """

    def set_hv_button_clicked(self, on: bool):
        """ Set high voltage output of the Dropbot Button clicked response """

    def get_channels_button_clicked(self):
        """ Get the current state of all channels from the Dropbot Button clicked response """

    def set_channels_button_clicked(self, channels):
        """ Set the state of all channels on the Dropbot Button clicked response """

    def set_channel_single_button_clicked(self, channel: int, state: bool):
        """ Set the state of a single channel on the Dropbot Button clicked response """

    def droplet_search_button_clicked(self, threshold: float = 0):
        """ Search for droplets on the Dropbot Button clicked response """

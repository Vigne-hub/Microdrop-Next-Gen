from traits.api import HasTraits, provides
from refrac_qt_microdrop.interfaces.event_hub_interface import IEventHubService
from refrac_qt_microdrop.helpers.logger import initialize_logger

logger = initialize_logger(__name__)


@provides(IEventHubService)
class EventHubService(HasTraits):

    def set_voltage_button_clicked(self, voltage, callback):
        try:
            self.dropbot_service.set_voltage(voltage)
            callback(f"Dropbot Status: Voltage set to {voltage}")
        except Exception as e:
            callback(f"Error setting voltage: {e}")

    def set_frequency_button_clicked(self, frequency, callback):
        try:
            self.dropbot_service.set_frequency(frequency)
            callback(f"Dropbot Status: Frequency set to {frequency}")
        except Exception as e:
            callback(f"Error setting frequency: {e}")

    def set_hv_button_clicked(self, on, callback):
        try:
            self.dropbot_service.set_hv(on)
            status = "enabled" if on else "disabled"
            callback(f"Dropbot Status: High voltage {status}")
        except Exception as e:
            callback(f"Error setting high voltage: {e}")

    def get_channels_button_clicked(self, callback):
        try:
            channels = self.dropbot_service.get_channels()
            callback(f"Dropbot Status: Channels {channels}")
        except Exception as e:
            callback(f"Error getting channels: {e}")
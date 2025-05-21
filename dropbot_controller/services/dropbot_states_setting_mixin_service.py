from traits.api import provides, HasTraits, Bool, Float

from microdrop_utils._logger import get_logger

from ..interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService


logger = get_logger(__name__, level="DEBUG")


@provides(IDropbotControlMixinService)
class DropbotStatesSettingMixinService(HasTraits):
    """
    A mixin Class that adds methods to set states for a dropbot connection and get some dropbot information.
    """

    id = "dropbot_states_setting_mixin_service"
    name = 'Dropbot States Setting Mixin'
    realtime_mode = Bool(False)
    voltage = Float(30)
    frequency = Float(1000)

    ######################################## Methods to Expose #############################################
    def on_set_voltage_request(self, message):
        """
        Method to set the voltage on the dropbot device.
        """
        try:
            voltage = float(message)
            self.voltage = voltage
            if self.realtime_mode:
                self.proxy.update_state(voltage=voltage)
            else:
                self.proxy.update_state(
                    hv_output_enabled=False,
                    voltage=voltage)
            logger.info(f"Set voltage to {voltage} V")
        except Exception as e:
            logger.error(f"Error setting voltage: {e}")
            raise

    def on_set_frequency_request(self, message):
        """
        Method to set the frequency on the dropbot device.
        """
        try:
            frequency = float(message)
            self.frequency = frequency
            if self.realtime_mode:
                self.proxy.update_state(frequency=frequency)
            else:
                self.proxy.update_state(
                    hv_output_enabled=False,
                    frequency=frequency)
            logger.info(f"Set frequency to {frequency} Hz")
        except Exception as e:
            logger.error(f"Error setting frequency: {e}")
            raise

    def on_set_realtime_mode_request(self, message):
        """
        Method to set the realtime mode on the dropbot device.
        """
        if message == "True":
            self.proxy.update_state(hv_output_selected=True,
                                    hv_output_enabled=True,
                                    voltage=self.voltage,
                                    frequency=self.frequency)
        else:
            self.proxy.update_state(hv_output_enabled=False)
        logger.info(f"Set realtime mode to {self.realtime_mode}")

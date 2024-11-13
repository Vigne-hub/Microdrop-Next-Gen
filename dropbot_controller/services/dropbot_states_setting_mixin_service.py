from traits.api import provides, HasTraits, Bool, Instance

from microdrop_utils._logger import get_logger

from ..interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService


logger = get_logger(__name__)


@provides(IDropbotControlMixinService)
class DropbotStatesSettingMixinService(HasTraits):
    """
    A mixin Class that adds methods to set states for a dropbot connection and get some dropbot information.
    """

    id = "dropbot_states_setting_mixin_service"
    name = 'Dropbot States Setting Mixin'

    ######################################## Methods to Expose #############################################
    def on_set_voltage_request(self, message):
        """
        Method to start looking for dropbots connected using their hwids.
        """

        self.proxy.voltage = float(message)

    def on_set_frequency_request(self, message):
        """
        Method to start looking for dropbots connected using their hwids.
        """

        self.proxy.frequency = float(message)


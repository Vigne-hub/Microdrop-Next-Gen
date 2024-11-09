import functools
import json

from collections.abc import Iterable


# unit handling
from pint import UnitRegistry

from dropbot_controller.interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

ureg = UnitRegistry()

from traits.api import provides, HasTraits

# microdrop utils imports
from microdrop_utils._logger import get_logger
logger = get_logger(__name__)


@provides(IDropbotControlMixinService)
class ElectrodeStateChangeMixinService(HasTraits):
    """
    A mixin Class that adds methods to change the electrode state in a dropbot.

    We assume that the base dropbot_controller plugin has been loaded with all of its services.
    So we should have access to the dropbot proxy object here, per the IDropbotControllerBase.
    """

    id = "electrode_state_change_mixin_service"
    name = 'Electrode state change Mixin'

    ######################################## Methods to Expose #############################################
    def on_electrode_state_change_request(self, message):
        """
        Method following the simple example in examples/tests/test_dropbot_methods to actuate electrodes on dropbot
        given the states and channels pairs in the JSON message as per model ChannelELectrodePairs.
        """
        message = json.loads(message)
        channels_states = message.get("channel_states", None)
        # do actuation
        self.proxy.state_of_channels = channels_states

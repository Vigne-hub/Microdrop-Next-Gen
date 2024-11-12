from traits.api import Instance, Bool
from microdrop_utils.dramatiq_dropbot_serial_proxy import DramatiqDropbotSerialProxy
from microdrop_utils.i_dramatiq_controller_base import IDramatiqControllerBase


class IDropbotControllerBase(IDramatiqControllerBase):
    """
    Interface for the Dropbot Controller Service.
    Provides methods for controlling and monitoring a Dropbot device.
    """

    proxy = Instance(DramatiqDropbotSerialProxy, desc="The DramatiqDropbotSerialProxy object")
    dropbot_connection_active = Bool(
        desc="Specifies if the controller is actively listening to commands or not. So if the dropbot "
             "connection is not there, no commands will be processed except searching for a dropbot "
             "connection"
    )

    def on_dropbot_signal(self, *args, **kwargs):
        """define some dropbot signal handlers:
        some signals are connected, disconnected, halted
        """

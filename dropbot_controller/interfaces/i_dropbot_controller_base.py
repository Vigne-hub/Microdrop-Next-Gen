from traits.api import Instance, Bool
from microdrop_utils.dramatiq_dropbot_serial_proxy import DramatiqDropbotSerialProxy
from microdrop_utils.i_dramatiq_controller_base import IDramatiqControllerBase


class IDropbotControllerBase(IDramatiqControllerBase):
    """
    Interface for the Dropbot Controller Service.
    Provides methods for controlling and monitoring a Dropbot device.
    """

    proxy = Instance(DramatiqDropbotSerialProxy, desc="The DramatiqDropbotSerialProxy object")
    active_state = Bool(desc="specifies if the controller is actively listening to commands or not")
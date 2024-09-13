import dramatiq
from traits.api import Interface, Instance

from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy


class IDropbotControllerBase(Interface):
    """
    Interface for the Dropbot Controller Service.
    Provides methods for controlling and monitoring a Dropbot device.
    """

    # Define the dropbot proxy object as an instance of DropbotSerialProxy
    proxy = Instance(DropbotSerialProxy)

    def traits_init(self):
        """
        Initialize the controller. Start monitoring for dropbot existence etc.
        """
        pass

    def create_actor_wrappers(self):
        """
        Create actor wrappers. For instance the dropbot backend listener actor.
        """
        pass

    def create_dropbot_backend_listener_actor(self) -> dramatiq.Actor:
        """
        Create a Dramatiq actor for listening to dropbot control related messages. For example requests from ui to
        affect dropbot in some way.

        Returns:
            dramatiq.Actor: The created Dramatiq actor.
        """
        pass

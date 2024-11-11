from traits.api import Instance
import dramatiq

from dropbot_controller.interfaces.i_dropbot_controller_base import IDropbotControllerBase

from traits.api import HasTraits, provides, Bool
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_dropbot_serial_proxy import DramatiqDropbotSerialProxy

logger = get_logger(__name__)


@provides(IDropbotControllerBase)
class DropbotControllerBase(HasTraits):
    proxy = Instance(DramatiqDropbotSerialProxy)
    listener = Instance(dramatiq.Actor, desc="Listener actor listens to messages sent to request dropbot backend services.")
    active_state = Bool(False)

    def traits_init(self):
        """
        This function needs to be here to let the listener be initialized to the default value automatically.
        We just do it manually here to make the code clearer.
        We can also do other initialization routines here if needed.

        This is equivalent to doing:

        def __init__(self, **traits):
            super().__init__(**traits)

        """
        logger.info("Starting DropbotControllerBase")
        self.listener = self._listener_default()

    def _listener_default(self) -> dramatiq.Actor:
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """
        @dramatiq.actor
        def dropbot_controller_listener(message, topic):
            """
            A Dramatiq actor that listens to messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.

            """
            logger.debug(f"DROPBOT BACKEND LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if "start_device_monitoring" == topic[-1] and self.active_state:
                logger.info("Dropbot controller already started")

            # Check if the method exists and call it
            elif hasattr(self, f"on_{topic[-1]}_request") and callable(getattr(self, f"on_{topic[-1]}_request")):
                # Use getattr to get the method and call it
                getattr(self, f"on_{topic[-1]}_request")(message)

            else:
                logger.warning(f"Method {topic[-1]} not found")

        return dropbot_controller_listener
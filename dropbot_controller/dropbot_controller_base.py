from traits.api import Instance
import dramatiq

from dropbot_controller.interfaces.i_dropbot_controller_base import IDropbotControllerBase

from traits.api import HasTraits, provides, Bool
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_dropbot_serial_proxy import DramatiqDropbotSerialProxy

logger = get_logger(__name__)


@provides(IDropbotControllerBase)
class DropbotControllerBase(HasTraits):
    # dropbot proxy object
    proxy = Instance(DramatiqDropbotSerialProxy)

    active_state = Bool()

    def traits_init(self):
        self.create_actor_wrappers()
        logger.info("Attempting to start DropBot monitoring")
        self.active_state = True
        self.on_start_device_monitoring_request(hwid_to_check="VID:PID=16C0:")

    def create_actor_wrappers(self):
        logger.debug("Creating actor wrappers")
        self.listener = self.create_listener_actor()

    def create_listener_actor(self):
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def dropbot_backend_listener(message, topic):
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

        return dropbot_backend_listener

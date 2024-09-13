from traits.api import Instance
import dramatiq

from dropbot_controller.interfaces.i_dropbot_controller_base import IDropbotControllerBase

from traits.api import HasTraits, provides
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


@provides(IDropbotControllerBase)
class DropbotControllerBase(HasTraits):
    # dropbot proxy object
    proxy = Instance(DropbotSerialProxy)

    def traits_init(self):
        self.create_actor_wrappers()
        logger.info("Attempting to start DropBot monitoring")
        self.start_device_monitoring(hwids_to_check=["VID:PID=16C0:"])

    def create_actor_wrappers(self):
        logger.debug("Creating actor wrappers")
        self.listener = self.create_dropbot_backend_listener_actor()

    def create_dropbot_backend_listener_actor(self):
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
            logger.info(f"DROPBOT BACKEND LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if topic[-1] == "disconnected":
                if not self.no_power:
                    self.on_disconnected()

            if topic[-1] == "detect_shorts_triggered":
                self.detect_shorts()

            if topic[-1] == "retry_connection_triggered":
                self.monitor_scheduler.resume()

        return dropbot_backend_listener

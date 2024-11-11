from PySide6.QtCore import Signal
from traits.api import Instance, HasTraits, provides
import dramatiq
import json

from microdrop_utils._logger import get_logger

logger = get_logger(__name__)

# local imports
from .widget import DropBotStatusWidget
from .interfaces.i_dramatiq_dropbot_status_controller import IDramatiqDropbotStatusController


@provides(IDramatiqDropbotStatusController)
class DramatiqDropbotStatusController(HasTraits):
    """Class to hook up the dropbot status widget signalling to a dramatiq system.
    Needs to be added as an attribute to a view.
    """

    listener = Instance(dramatiq.Actor)
    view = Instance(DropBotStatusWidget, desc="The DropbotStatusWidget object")

    def traits_init(self):
        """ Initialize everything """

        self.listener = self._listener_default()

    def _listener_default(self):
        """
        Listen to Topics being triggered to affect UI and emit signal.
        We are using signals since pyside6 widgets are used. signals and splots mechanism seems to work better
        than using callbacks that are setup manually.
        """

        @dramatiq.actor
        def dropbot_status_listener(message, topic):
            logger.debug(f"UI_LISTENER: Received message: {message} from topic: {topic}. Triggering UI Signal")
            self.view.controller_signal.emit(json.dumps({'message': message, 'topic': topic}))

        return dropbot_status_listener

    def controller_signal_handler(self, signal):
        """
        Handle GUI action required for signal triggered by dropbot status listener.
        """
        signal = json.loads(signal)
        topic = signal.get("topic", "")
        message = signal.get("message", "")
        head_topic = topic.split('/')[-1]
        sub_topic = topic.split('/')[-2]
        method = f"_on_{head_topic}_triggered"

        if hasattr(self.view, method) and callable(getattr(self.view, method)):
            logger.debug(f"Method for {head_topic}, {method} getting called.")
            getattr(self.view, method)(message)

        # special topic warnings. Catch them all and print out to screen. Generic method for all warnings in case no
        # specific implementations for them defined.
        elif sub_topic == "warnings":
            logger.info(f"Warning triggered. No special method for warning {head_topic}. Generic message produced")

            title = head_topic.replace('_', ' ').title()

            self.view._on_show_warning_triggered(json.dumps(

                {'title': title,
                 'message': message}
            ))

        else:
            logger.warning(f"Method for {head_topic}, {method} not found.")
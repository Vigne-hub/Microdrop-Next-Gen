from traits.api import HasTraits, provides, Str
import dramatiq
import json
from traits.api import Instance

from dropbot_controller.consts import START_DEVICE_MONITORING
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_controller_base import generate_class_method_dramatiq_listener_actor
from microdrop_utils.base_dropbot_qwidget import BaseDramatiqControllableDropBotQWidget
from microdrop_utils.dramatiq_controller_base import invoke_class_method
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

logger = get_logger(__name__)

# local imports
from .interfaces.i_dramatiq_dropbot_status_controller import IDramatiqDropbotStatusController


@provides(IDramatiqDropbotStatusController)
class DramatiqDropbotStatusController(HasTraits):
    """Class to hook up the dropbot status widget signalling to a dramatiq system.
    Needs to be added as an attribute to a view.
    """

    view = Instance(BaseDramatiqControllableDropBotQWidget, desc="The DropbotStatusWidget object")

    ##########################################################
    # 'IDramatiqControllerBase' interface.
    ##########################################################

    dramatiq_listener_actor = Instance(dramatiq.Actor)

    # This class is not immediately initialized here as in device viewer and in dropbot controller
    # this can be set later by whatever UI view that uses it
    listener_name = Str(desc="Unique identifier for the Dramatiq actor")

    def listener_actor_routine(self, message, topic):
        logger.debug(f"UI_LISTENER: Received message: {message} from topic: {topic}. Triggering UI Signal")
        self.view.controller_signal.emit(json.dumps({'message': message, 'topic': topic}))

    def traits_init(self):
        """
        This function needs to be here to let the listener be initialized to the default value automatically.
        We just do it manually here to make the code clearer.
        We can also do other initialization routines here if needed.

        This is equivalent to doing:

        def __init__(self, **traits):
            super().__init__(**traits)

        """

        logger.info("Starting Device listener")
        self.dramatiq_listener_actor = generate_class_method_dramatiq_listener_actor(
            listener_name=self.listener_name,
            class_method=self.listener_actor_routine)

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

        err_msg = invoke_class_method(self.view, method, message)
        if err_msg:

            # special topic warnings. Catch them all and print out to screen. Generic method for all warnings in case no
            # specific implementations for them defined.
            if sub_topic == "warnings":
                logger.info(f"Warning triggered. No special method for warning {head_topic}. Generic message produced")

                title = head_topic.replace('_', ' ').title()

                self.view._on_show_warning_triggered(json.dumps(

                    {'title': title,
                     'message': message}
                ))

            else:
                logger.debug(f"Method for {head_topic}, {method} not executed: Error: {err_msg}")
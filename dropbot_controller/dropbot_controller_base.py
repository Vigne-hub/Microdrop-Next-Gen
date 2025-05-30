import json

from dropbot import EVENT_CHANNELS_UPDATED, EVENT_SHORTS_DETECTED, EVENT_ENABLE
from traits.api import Instance
import dramatiq

# unit handling
from pint import UnitRegistry

from microdrop_utils.dramatiq_controller_base import generate_class_method_dramatiq_listener_actor, invoke_class_method

ureg = UnitRegistry()

from .consts import (CHIP_INSERTED, CHIP_NOT_INSERTED, CAPACITANCE_UPDATED, HALTED, HALT, START_DEVICE_MONITORING,
                     RETRY_CONNECTION, OUTPUT_ENABLE_PIN, SHORTS_DETECTED, PKG)

from .interfaces.i_dropbot_controller_base import IDropbotControllerBase

from traits.api import HasTraits, provides, Bool
from microdrop_utils.dramatiq_dropbot_serial_proxy import DramatiqDropbotSerialProxy, CONNECTED, DISCONNECTED
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

from microdrop_utils._logger import get_logger

logger = get_logger(__name__)


@provides(IDropbotControllerBase)
class DropbotControllerBase(HasTraits):
    """
    This class provides some methods for handling signals from the proxy. But mainly provides a dramatiq listener
    that captures appropriate signals and calls the methods needed.
    """
    proxy = Instance(DramatiqDropbotSerialProxy)
    dropbot_connection_active = Bool(False)

    ##########################################################
    # 'IDramatiqControllerBase' interface.
    ##########################################################

    dramatiq_listener_actor = Instance(dramatiq.Actor)

    listener_name = f"{PKG}_listener"

    def listener_actor_routine(self, message, topic):
        """
        A Dramatiq actor that listens to messages.

        Parameters:
        message (str): The received message.
        topic (str): The topic of the message.

        """

        # logger.info(f"DROPBOT BACKEND LISTENER: Received message: '{message}' from topic: '{topic}'")

        # find the topics hierarchy: first element is the head topic. Last element is the specific topic
        topics_tree = topic.split("/")
        head_topic = topics_tree[0]
        primary_sub_topic = topics_tree[1]
        specific_sub_topic = topics_tree[-1]

        # set requested method to None for now
        requested_method = None

        # Determine the requested method to call based on the topic, if it is a dropbot request or signal topic
        # for external dropbot signals connected/disconnected, we handle them everytime. For requests,
        # we need to check if we have a dropbot available or not. Unless it is a request to start looking for a
        # device or disconnect the device.

        # 1. Check if it is a dropbot related topic
        if head_topic == 'dropbot':

            # 2. Handle the connected / disconnected signals
            if topic in [CONNECTED, DISCONNECTED]:
                requested_method = f"on_{specific_sub_topic}_signal"

            # 3. Handle specific dropbot requests that would change dropbot connectivity
            ## 3.1. Request to activate dropbot connection
            elif topic in [START_DEVICE_MONITORING, RETRY_CONNECTION]:
                if self.dropbot_connection_active:
                    logger.warning(
                        "Redundant request to start device monitoring denied: Dropbot is already connected."
                        "Publishing message to UI about dropbot chip insertion status.")
                    if not self.proxy.digital_read(OUTPUT_ENABLE_PIN):
                        publish_message(topic=CHIP_INSERTED, message='Chip inserted')
                    else:
                        publish_message(topic=CHIP_NOT_INSERTED, message='Chip not inserted')

                else:
                    requested_method = f"on_{specific_sub_topic}_request"
                    logger.info(f"Executing {specific_sub_topic} method as Dropbot is currently disconnected.")

            # 4. Handle all other requests
            elif primary_sub_topic == 'requests':
                if self.dropbot_connection_active:
                    requested_method = f"on_{specific_sub_topic}_request"
                else:
                    logger.warning(f"Request for {specific_sub_topic} denied: Dropbot is disconnected.")

        else:
            logger.info(f"Ignored request from topic '{topic}': Not a Dropbot-related request.")

        if requested_method:
            err_msg = invoke_class_method(self, requested_method, message)

            if err_msg:
                logger.error(
                    f" {self.listener_name}; Received message: {message} from topic: {topic} Failed to execute due to "
                    f"error: {err_msg}")

    def traits_init(self):
        """
        This function needs to be here to let the listener be initialized to the default value automatically.
        We just do it manually here to make the code clearer.
        We can also do other initialization routines here if needed.

        This is equivalent to doing:

        def __init__(self, **traits):
            super().__init__(**traits)

        """

        logger.info("Starting DropbotController listener")
        self.dramatiq_listener_actor = generate_class_method_dramatiq_listener_actor(
            listener_name=self.listener_name,
            class_method=self.listener_actor_routine)

    ######################################################################
    # Proxy signal handlers
    #######################################################################

    # proxy signal handlers done this way so that these methods can be overrided externally

    def _on_dropbot_proxy_connected(self):
        # do initial check on if chip inserted or not
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            logger.info("Publishing Chip Not Inserted")
            publish_message(topic=CHIP_NOT_INSERTED, message='Chip not inserted')
        else:
            logger.info("Publishing Chip inserted")
            publish_message(topic=CHIP_INSERTED, message='Chip inserted')
            self.on_detect_shorts_request("")

        self.proxy.signals.signal('output_enabled').connect(self._output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self._output_state_changed_wrapper)
        self.proxy.signals.signal('halted').connect(self._halted_event_wrapper, weak=False)
        self.proxy.signals.signal('capacitance-updated').connect(self._capacitance_updated_wrapper)
        self.proxy.signals.signal('shorts-detected').connect(self._shorts_detected_wrapper)

        # Initial Proxy State Update
        self.proxy.update_state(capacitance_update_interval_ms=250,
                                event_mask=EVENT_CHANNELS_UPDATED |
                                           EVENT_SHORTS_DETECTED |
                                           EVENT_ENABLE)
        # If the feedback capacitor is < 300nF, disable the chip load
        # saturation check to prevent false positive triggers.
        if self.proxy.config.C16 < 0.3e-6:
            self.proxy.update_state(chip_load_range_margin=-1)

        self.proxy.update_state(hv_output_selected=True,
                                hv_output_enabled=True,
                                voltage=75,
                                )

        self.proxy.turn_off_all_channels()

    @staticmethod
    def _capacitance_updated_wrapper(signal: dict[str, str]):
        capacitance = float(signal.get('new_value', 0.0)) * ureg.farad
        capacitance_formatted = f"{capacitance.to(ureg.picofarad):.4g~P}"
        voltage = float(signal.get('V_a', 0.0)) * ureg.volt
        voltage_formatted = f"{voltage:.3g~P}"
        publish_message(topic=CAPACITANCE_UPDATED,
                        message=json.dumps({'capacitance': capacitance_formatted, 'voltage': voltage_formatted}))

    @staticmethod
    def _shorts_detected_wrapper(signal: dict[str, str]):
        shorts_list = signal.get('values')
        shorts_dict = {'Shorts_detected': shorts_list}
        publish_message(topic=SHORTS_DETECTED, message=json.dumps(shorts_dict))

    @staticmethod
    def _halted_event_wrapper(signal):

        reason = ''

        if signal['error']['name'] == 'output-current-exceeded':
            reason = 'because output current was exceeded'
        elif signal['error']['name'] == 'chip-load-saturated':
            reason = 'because chip load feedback exceeded allowable range'

        # send out signal to all interested parties that the dropbot has been halted and request the HALT method
        publish_message(topic=HALTED, message=reason)
        publish_message(topic=HALT, message="")

        logger.error(f'DropBot halted due to {reason}')

    @staticmethod
    def _output_state_changed_wrapper(signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            logger.info("Publishing Chip Inserted")
            publish_message(topic=CHIP_INSERTED, message='Chip inserted')
        elif signal['event'] == 'output_disabled':
            logger.info("Publishing Chip Not Inserted")
            publish_message(topic=CHIP_NOT_INSERTED, message='Chip not inserted')
        else:
            logger.warn(f"Unknown signal received: {signal}")

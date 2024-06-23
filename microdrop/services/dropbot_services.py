import functools
import json
import re
import sys
from typing import Union

import dramatiq
import dropbot
import numpy as np
from PySide6.QtWidgets import QApplication
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dramatiq import get_broker, Worker
from nptyping import NDArray, Shape, UInt8
from serial.tools.list_ports import grep
from traits.has_traits import HasTraits, provides

from microdrop.interfaces import IDropbotControllerService
from microdrop.plugins.frontend_plugins.dropbot_status.qt_widget import DropBotControlWidget
from microdrop.pydantic_models.dropbot_controller_signals import DBVoltageChangedModel, \
    DBChannelsMetastateChanged, DBChannelsChangedModel, DBConnectionStateModel, \
    DBChipInsertStateModel, DBErrorModel
from microdrop.services.dropbot_service_helpers import check_dropbot_devices_available
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


@provides(IDropbotControllerService)
class DropbotService(HasTraits):

    def __init__(self):
        logger.info('Initializing dropbot services')

        self.make_serial_proxy = self._make_serial_proxy()
        self.ui_listener = self.create_dropbot_backend_listener_actor()

        # actor_topics
        self.actor_topics_dict = {"dropbot_backend_listener": ["dropbot/signals/#", "dropbot/ui/notifications/#"]}

        self.proxy: Union[DropbotSerialProxy, None] = None

        hwids_to_check = ["VID:PID=16C0:"]

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=2),
        )
        scheduler.add_listener(self.on_dropbot_port_found, EVENT_JOB_EXECUTED)
        self.scheduler = scheduler

    @staticmethod
    def emit_signal(message):
        # assume message is already in json format
        publish_message(message, f'dropbot_controller/signals/{message.Signal}')
        logger.info(f"Emitted: {message}")

    #### Dropbot mike actions ####
    @dramatiq.actor
    def poll_voltage(self):
        """
        Periodically polls for the current voltage from the Dropbot and emits
        the `voltage_changed` signal with the fetched voltage value.
        """
        if self.proxy is not None:
            try:
                voltage = self.proxy.high_voltage()
                self.emit_signal(DBVoltageChangedModel(Signal='voltage_changed', voltage=str(voltage)))
            except OSError:  # No dropbot connected
                pass

    @dramatiq.actor
    def set_voltage(self, voltage: int):
        """
        Sets the voltage of the Dropbot to the specified value.

        Args:
            voltage (int): Desired voltage setting.
        """
        logger.debug(f"Setting voltage to {voltage}")
        if self.proxy is not None:
            self.proxy.voltage = voltage
        logger.info("Voltage set to %d", voltage)

    @dramatiq.actor
    def set_frequency(self, frequency: int):
        """
        Sets the frequency of the Dropbot to the specified value.

        Args:
            frequency (int): Desired frequency setting.
        """
        logger.debug(f"Setting frequency to {frequency}")
        if self.proxy is not None:
            self.proxy.frequency = frequency
        logger.info("Frequency set to %d", frequency)

    @dramatiq.actor
    def set_hv(self, on: bool):
        """
        Enables or disables the high voltage output of the Dropbot.

        Args:
            on (bool): True to enable high voltage, False to disable.
        """
        if self.proxy is not None:
            self.proxy.hv_output_enabled = on

    @dramatiq.actor
    def get_channels(self) -> NDArray[Shape['*, 1'], UInt8]:
        """
        Retrieves and returns the current state of all channels from the Dropbot,
        emitting a signal if there is a change from the last known state.

        Returns:
            NDArray[Shape['*, 1'], UInt8]: The current state of the channels.
        """
        if self.proxy is None:
            return np.zeros(128, dtype='uint8')

        channels = np.array(self.proxy.state_of_channels)
        if (self.last_state != channels).any():
            self.last_state = channels
            self.emit_signal(DBChannelsChangedModel(Signal='channels_changed', channels=str(channels)))
        return channels

    @dramatiq.actor
    def set_channels(self, channels: NDArray[Shape['*, 1'], UInt8]):
        """
        Sets the state of all channels in the Dropbot to the specified array and
        updates the last known state.

        Args:
            channels (NDArray[Shape['*, 1'], UInt8]): An array representing the desired
            state of all channels.
        """
        if self.proxy is None:
            return
        self.proxy.state_of_channels = np.array(channels)
        self.last_state = self.get_channels()

    @dramatiq.actor
    def set_channel_single(self, channel: int, state: bool):
        """
        Sets the state of a single channel.

        Args:
            channel (int): Index of the channel to be modified.
            state (bool): Desired state (True for enabled, False for disabled).
        """
        if self.proxy is None:
            return
        channels = self.get_channels()
        channels[channel] = state
        self.set_channels(channels)

    @dramatiq.actor
    def droplet_search(self, threshold: float = 0):
        """
        Searches for droplets above a specified capacitance threshold and updates
        the metastate of the channels accordingly.

        Args:
            threshold (float, optional): Capacitance threshold for identifying droplets.
            Defaults to 0.
        """
        if self.proxy is not None:
            # Disable all electrodes
            self.set_channels(np.zeros_like(self.last_state))

            drops = list(self.last_state)
            for drop in self.proxy.get_drops(capacitance_threshold=threshold):
                for electrode in drop:
                    drops[electrode] = 'droplet'

            self.emit_signal(DBChannelsMetastateChanged(Signal='channels_metastate_changed', Drops=str(drops)))
    ##############################

    def on_dropbot_port_found(self, event):
        logger.info("DropBot port found")
        logger.info('Attempting to make serial proxy for DropBot')
        self.scheduler.pause()
        port_name = str(event.retval)
        self.make_serial_proxy.send(port_name)

    def on_disconnected(self):
        self.scheduler.resume()
        publish_message(topic='dropbot/ui/signals/disconnected', message='DropBot disconnected')

    def on_connected(self):
        self.scheduler.pause()
        publish_message(topic='dropbot/ui/signals/connected', message='DropBot connected')

    def _make_serial_proxy(self):
        logger.info("Creating serial proxy function")

        @dramatiq.actor
        def make_serial_proxy(port_name):
            logger.info(f"Attempting to create serial proxy")
            try:
                self.proxy = DropbotSerialProxy(port=port_name)
                logger.info(f"Connected to DropBot on port {port_name}")
                self.setup_dropbot()
            except (IOError, AttributeError):
                publish_message(topic='dropbot/ui/connection/warnings/no_dropbot_available',
                                message='No DropBot available for connection')
                logger.error("No DropBot available for connection")
            except dropbot.proxy.NoPower:
                publish_message(topic='dropbot/ui/connection/warnings/no_power', message='No power to DropBot')
                logger.error("No power to DropBot")

        logger.info('Completed making serial proxy')
        return make_serial_proxy

    def create_dropbot_backend_listener_actor(self):
        """
        Create a Dramatiq actor for listening to UI-related messages.

        Returns:
        dramatiq.Actor: The created Dramatiq actor.
        """

        @dramatiq.actor
        def dropbot_backend_listener(message, topic):
            """
            A Dramatiq actor that listens to UI-related messages.

            Parameters:
            message (str): The received message.
            topic (str): The topic of the message.
            """
            logger.info(f"DROPBOT BACKEND LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if topic[-1] == "connected":
                self.on_connected()

            if topic[-1] == "disconnected":
                if self.proxy is not None:
                    if self.proxy.monitor is not None:
                        self.proxy.terminate()
                        self.proxy.monitor = None
                        self.on_disconnected()
                else:
                    print("Proxy is None")

            if topic[-1] == "detect_shorts_triggered":
                self.detect_shorts()

        return dropbot_backend_listener

    def setup_dropbot(self):
        OUTPUT_ENABLE_PIN = 22
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            publish_message(topic='dropbot/ui/signals/chip_not_inserted', message='Chip not inserted')
        else:
            publish_message(topic='dropbot/ui/signals/chip_inserted', message='Chip inserted')

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('halted').connect(self.halted_event_wrapper)
        self.proxy.signals.signal('shorts-detected').connect(self.shorts_detected_event_wrapper)

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            publish_message(topic='dropbot/ui/signals/chip_inserted', message='Chip inserted')
        elif signal['event'] == 'output_disabled':
            publish_message(topic='dropbot/ui/signals/chip_not_inserted', message='Chip not inserted')
        else:
            logger.warn(f"Unknown signal received: {signal}")

    def halted_event_wrapper(self, signal: dict[str, str]):
        publish_message(topic='dropbot/ui/signals/halted', message='DropBot halted')

    def shorts_detected_event_wrapper(self, signal: dict[str, str]):
        publish_message(topic='dropbot/ui/signals/shorts_detected', message='Shorts detected')

    def detect_shorts(self):
        if self.proxy is not None:
            shorts_list = self.proxy.detect_shorts()
            shorts_dict = {'Shorts_detected': shorts_list}
            publish_message(topic='dropbot/ui/signals/shorts_detected', message=json.dumps(shorts_dict))

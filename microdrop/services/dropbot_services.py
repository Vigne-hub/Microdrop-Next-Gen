import functools
import json
import re
import sys
import threading
from typing import Union

import dramatiq
import dropbot
import numpy as np

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dramatiq import get_broker, Worker
from dropbot import EVENT_CHANNELS_UPDATED, EVENT_SHORTS_DETECTED, EVENT_ENABLE
from nptyping import NDArray, Shape, UInt8
from traits.has_traits import HasTraits, provides

from microdrop.interfaces import IDropbotControllerService
from microdrop.services.dropbot_service_helpers import check_dropbot_devices_available
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


@provides(IDropbotControllerService)
class DropbotService(HasTraits):

    def __init__(self):
        self.connected = False
        self.chip_inserted = False
        self.power_in = False

        # actor_topics
        self.actor_topics_dict = {
            "dropbot_backend_listener": ["dropbot/ui/notifications/#",
                                         "dropbot/signals/disconnected",
                                         "dropbot/signals/halted"]}

        self.proxy: Union[DropbotSerialProxy, None] = None
        self.create_actor_wrappers()

        logger.info("Attempting to start DropBot monitoring")
        self.start_device_monitoring(hwids_to_check=["VID:PID=16C0:"])

    def create_actor_wrappers(self):
        logger.debug("Creating actor wrappers")
        self.ui_listener = self.create_dropbot_backend_listener_actor()
        pass  # add actor wrappers here

    def start_device_monitoring(self, hwids_to_check):
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=2),
        )

        scheduler.add_listener(self.on_dropbot_port_found, EVENT_JOB_EXECUTED)
        self.monitor_scheduler = scheduler
        logger.info("DropBot monitor created")
        logger.info("Starting DropBot monitor")
        self.monitor_scheduler.start()

    def on_dropbot_port_found(self, event):
        logger.info("DropBot port found")
        self.monitor_scheduler.pause()
        logger.info("Paused DropBot monitor")
        port_name = str(event.retval)
        logger.info('Attempting to connect to DropBot on port: %s', port_name)
        self.connect_to_dropbot(port_name)

    def connect_to_dropbot(self, port_name):
        """
        Once a port is found, attempt to connect to the DropBot on that port.

        IF already connected, do nothing.
        IF not connected, attempt to connect to the DropBot on the port.

        FAIL IF:
        - No DropBot available for connection - USB not connected
        - No power to DropBot - power supply not connected
        """

        if not self.connected:
            logger.info("Dropbot not connected. Attempting to connect")
            try:
                logger.info(f"Attempting to create DropBot serial proxy on port {port_name}")
                self.proxy = DropbotSerialProxy(port=port_name)
                self.connected = True
                logger.info(f"Connected to DropBot on port {port_name}")
                logger.info(f"Checking if chip is inserted AND connecting DropBot BLINKER signals to handlers")
                self.setup_dropbot()  # Setup the DropBot especially blinker signal trigger follow-up methods

                # Initial Proxy State Update
                self.proxy.update_state(capacitance_update_interval_ms=1000,
                                        hv_output_selected=True,
                                        hv_output_enabled=True,
                                        voltage=75,
                                        event_mask=EVENT_CHANNELS_UPDATED |
                                                   EVENT_SHORTS_DETECTED |
                                                   EVENT_ENABLE)
            except (IOError, AttributeError):
                self.connected = False
                publish_message(topic='dropbot/signals/connection/warnings/no_dropbot_available',
                                message='No DropBot available for connection')
                logger.error("FAILED DROPBOT CONNECTION: No DropBot available for connection")
            except dropbot.proxy.NoPower:
                self.connected = False
                publish_message(topic='dropbot/signals/connection/warnings/no_power', message='No power to DropBot')
                logger.error("FAILED DROPBOT CONNECTION: No power to DropBot")
        else:
            logger.info("Dropbot already connected on port %s", port_name)

    def setup_dropbot(self):
        OUTPUT_ENABLE_PIN = 22
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            publish_message(topic='dropbot/signals/chip_not_inserted', message='Chip not inserted')
        else:
            publish_message(topic='dropbot/signals/chip_inserted', message='Chip inserted')
            self.detect_shorts()

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('halted').connect(self.halted_event_wrapper)
        self.proxy.monitor.signals.signal('capacitance-updated').connect(self.capacitance_updated_wrapper)

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            publish_message(topic='dropbot/signals/chip_inserted', message='Chip inserted')
        elif signal['event'] == 'output_disabled':
            publish_message(topic='dropbot/signals/chip_not_inserted', message='Chip not inserted')
        else:
            logger.warn(f"Unknown signal received: {signal}")

    def halted_event_wrapper(self):
        print("DropBot halted")
        publish_message(topic='dropbot/signals/halted', message='DropBot halted')

    def capacitance_updated_wrapper(self, signal: dict[str, str]):
        capacitance = self.format_significant_digits(signal['new_value'], 4)
        voltage = str(round(float(signal['V_a']), 2))
        publish_message(topic='dropbot/signals/capacitance_updated',
                        message=json.dumps({'capacitance': capacitance, 'voltage': voltage}))

    def on_disconnected(self):
        logger.info(
            "DropBot disconnected \n Attempting to terminate proxy and resume monitoring to find DropBot again.")
        if self.connected:
            if self.proxy is not None:
                if self.proxy.monitor is not None:
                    self.connected = False
                    self.proxy.terminate()
                    logger.info("Proxy terminated")
                    self.proxy.monitor = None

                    self.monitor_scheduler.resume()
                    logger.info("Resumed DropBot monitor")
            else:
                logger.info("Proxy is None")
        else:
            logger.info("Dropbot already disconnected")

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

            if topic[-1] == "disconnected":
                self.on_disconnected()

            if topic[-1] == "detect_shorts_triggered":
                self.detect_shorts()

        return dropbot_backend_listener

    ####### Follow Up Methods to Signals Sent Outside of Dropbot Services #######
    def detect_shorts(self):
        if self.proxy is not None:
            shorts_list = self.proxy.detect_shorts()
            shorts_dict = {'Shorts_detected': shorts_list}
            publish_message(topic='dropbot/signals/shorts_detected', message=json.dumps(shorts_dict))

    ##############################################################################

    def format_significant_digits(self, number_str, significant_digits):
        # Convert the string to a float
        number = float(number_str)
        # Format the number to keep a specified number of significant digits without scientific notation
        if number == 0:
            return '0.' + '0' * (significant_digits - 1)  # Handle the case where number is zero
        else:
            formatted_num = f"{number:.{significant_digits}g}"
            formatted_num = formatted_num[:-4]
            while len(formatted_num) < significant_digits + 1:
                formatted_num += '0'
            return formatted_num

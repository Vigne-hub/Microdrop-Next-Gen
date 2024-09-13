import functools
import json

import dropbot
from traits.api import provides, HasTraits, Dict, Str
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dropbot import EVENT_CHANNELS_UPDATED, EVENT_SHORTS_DETECTED, EVENT_ENABLE

from microdrop_utils.dramatiq_pub_sub_helpers import publish_message
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy
from microdrop_utils.dropbot_monitoring_helpers import check_dropbot_devices_available
from ..interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

from ..pub_sub_topics import NO_DROPBOT_AVAILABLE, CHIP_INSERTED, CHIP_NOT_INSERTED, HALTED, \
    CAPACITANCE_UPDATED, SHORTS_DETECTED, NO_POWER

logger = get_logger(__name__)


@provides(IDropbotControlMixinService)
class DropbotMonitorMixinService(HasTraits):
    """
    A mixin Class that adds methods to monitor a dropbot connection and get some dropbot information.
    """

    id = "dropbot_monitor_mixin_service"
    name = 'Dropbot Monitor Mixin'

    ######################################## Methods to Expose #############################################
    def start_device_monitoring(self, hwids_to_check):
        """
        Method to start looking for dropbots connected using their hwids.
        """
        self.halted_check_scheduler = BackgroundScheduler()
        self.halted_check_scheduler.add_job(self._check_halted, trigger=IntervalTrigger(seconds=2))

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=2),
        )

        scheduler.add_listener(self._on_dropbot_port_found, EVENT_JOB_EXECUTED)
        self.monitor_scheduler = scheduler
        logger.info("DropBot monitor created")
        logger.info("Starting DropBot monitor")
        self.monitor_scheduler.start()

    def detect_shorts(self):
        if self.proxy is not None:
            shorts_list = self.proxy.detect_shorts()
            shorts_dict = {'Shorts_detected': shorts_list}
            publish_message(topic=SHORTS_DETECTED, message=json.dumps(shorts_dict))

    def on_disconnected(self):
        logger.info(
            "DropBot disconnected \n Attempting to terminate proxy and resume monitoring to find DropBot again.")

        if self.proxy is not None:
            if self.proxy.monitor is not None:
                self.proxy.terminate()
                logger.info("Proxy terminated")
                self.proxy.monitor = None
                self.monitor_scheduler.resume()
                logger.info("Resumed DropBot monitor")

    ################################# Protected methods ######################################
    def _on_dropbot_port_found(self, event):
        """
        Method defining what to do when dropbot has been found on a port.
        """
        logger.info("DropBot port found")
        self.monitor_scheduler.pause()
        logger.info("Paused DropBot monitor")
        self.port_name = str(event.retval)
        logger.info('Attempting to connect to DropBot on port: %s', self.port_name)
        self._connect_to_dropbot(port_name=self.port_name)

    def _connect_to_dropbot(self, port_name):
        """
        Once a port is found, attempt to connect to the DropBot on that port.

        IF already connected, do nothing.
        IF not connected, attempt to connect to the DropBot on the port.

        FAIL IF:
        - No DropBot available for connection - USB not connected
        - No power to DropBot - power supply not connected
        """

        if self.proxy is None or getattr(self, 'proxy.monitor', None) is None:

            logger.info("Dropbot not connected. Attempting to connect")

            ############################### Attempt to make a proxy object #############################

            try:
                logger.info(f"Attempting to create DropBot serial proxy on port {port_name}")
                self.proxy = DropbotSerialProxy(port=port_name)
                # this will send out a connected signal to the message router is successful

            except (IOError, AttributeError):

                publish_message(topic=NO_DROPBOT_AVAILABLE,
                                message='No DropBot available for connection')
                logger.error("FAILED DROPBOT CONNECTION: No DropBot available for connection")

            except dropbot.proxy.NoPower:
                self._on_no_power()

            ################################# Post connection steps ###################################

            self.no_power = False
            logger.info(f"Connected to DropBot on port {port_name}")
            logger.info(f"Checking if chip is inserted AND connecting DropBot BLINKER signals to handlers")
            self._setup_dropbot()  # Setup the DropBot especially blinker signal trigger follow-up methods

            # Initial Proxy State Update
            self.proxy.update_state(capacitance_update_interval_ms=1000,
                                    hv_output_selected=True,
                                    hv_output_enabled=True,
                                    voltage=75,
                                    event_mask=EVENT_CHANNELS_UPDATED |
                                               EVENT_SHORTS_DETECTED |
                                               EVENT_ENABLE)

            if self.halted_check_scheduler.running:
                self.halted_check_scheduler.resume()
            else:
                self.halted_check_scheduler.start()

        # if the dropbot is already connected
        else:
            logger.info("Dropbot already connected on port %s", port_name)

    def _setup_dropbot(self):
        OUTPUT_ENABLE_PIN = 22
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            publish_message(topic=CHIP_INSERTED, message='Chip not inserted')
        else:
            publish_message(topic=CHIP_NOT_INSERTED, message='Chip inserted')
            self.detect_shorts()

        self.proxy.signals.signal('output_enabled').connect(self._output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self._output_state_changed_wrapper)
        self.proxy.signals.signal('halted').connect(self._halted_event_wrapper)
        self.proxy.signals.signal('capacitance-updated').connect(self._capacitance_updated_wrapper)

    def _capacitance_updated_wrapper(self, signal: dict[str, str]):
        capacitance = float(signal['new_value']) * self.ureg.farad
        capacitance_formatted = f"{capacitance.to(self.ureg.picofarad):.2g~P}"
        voltage = float(signal['V_a']) * self.ureg.volt
        voltage_formatted = f"{voltage:.2g~P}"
        publish_message(topic=CAPACITANCE_UPDATED,
                        message=json.dumps({'capacitance': capacitance_formatted, 'voltage': voltage_formatted}))

    def _check_halted(self):
        if self.proxy is not None:
            # the dropbot is halted if the high voltage output is not enabled and the realtime is enabled
            if not self.proxy.hv_output_enabled and self.realtime_enabled:
                publish_message(topic=HALTED, message='DropBot halted')
                self.halted_check_scheduler.pause()
            else:
                pass
        else:
            pass

    @staticmethod
    def _halted_event_wrapper():
        print("DropBot halted")
        publish_message(topic=HALTED, message='DropBot halted')

    @staticmethod
    def _output_state_changed_wrapper(signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            publish_message(topic=CHIP_INSERTED, message='Chip inserted')
        elif signal['event'] == 'output_disabled':
            publish_message(topic=CHIP_NOT_INSERTED, message='Chip not inserted')
        else:
            logger.warn(f"Unknown signal received: {signal}")

    @staticmethod
    def _on_no_power():
        publish_message(topic=NO_POWER, message='No power to DropBot')
        logger.error("FAILED DROPBOT CONNECTION: No power to DropBot")
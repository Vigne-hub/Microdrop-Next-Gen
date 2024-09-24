import functools
import json

import dropbot
from traits.api import provides, HasTraits, Bool
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dropbot import EVENT_CHANNELS_UPDATED, EVENT_SHORTS_DETECTED, EVENT_ENABLE

from microdrop_utils.dramatiq_pub_sub_helpers import publish_message
from microdrop_utils._logger import get_logger
from microdrop_utils.dramatiq_dropbot_serial_proxy import DramatiqDropbotSerialProxy
from microdrop_utils.dropbot_monitoring_helpers import check_dropbot_devices_available
from ..interfaces.i_dropbot_control_mixin_service import IDropbotControlMixinService

from ..consts import NO_DROPBOT_AVAILABLE, CHIP_INSERTED, CHIP_NOT_INSERTED, HALTED, \
    CAPACITANCE_UPDATED, SHORTS_DETECTED, NO_POWER, DROPBOT_DB3_120_HWID, OUTPUT_ENABLE_PIN

logger = get_logger(__name__)


@provides(IDropbotControlMixinService)
class DropbotMonitorMixinService(HasTraits):
    """
    A mixin Class that adds methods to monitor a dropbot connection and get some dropbot information.
    """

    id = "dropbot_monitor_mixin_service"
    name = 'Dropbot Monitor Mixin'
    realtime_mode = Bool(True)

    ######################################## Methods to Expose #############################################
    def on_start_device_monitoring_request(self, hwid_to_check):
        """
        Method to start looking for dropbots connected using their hwids.
        """

        if not hwid_to_check:
            hwid_to_check = DROPBOT_DB3_120_HWID

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwid_to_check),
            trigger=IntervalTrigger(seconds=2),
        )
        scheduler.add_listener(self._on_dropbot_port_found, EVENT_JOB_EXECUTED)
        self.monitor_scheduler = scheduler

        logger.info("DropBot monitor created and started")

        self.monitor_scheduler.start()

    def on_detect_shorts_request(self, message):
        if self.proxy is not None:
            shorts_list = self.proxy.detect_shorts()
            shorts_dict = {'Shorts_detected': shorts_list}
            logger.info(f"Detected shorts: {shorts_dict}")
            publish_message(topic=SHORTS_DETECTED, message=json.dumps(shorts_dict))

    def on_disconnected_request(self, message):

        if not self._no_power:
            logger.info(
                "DropBot disconnected \n Attempting to terminate proxy and resume monitoring to find DropBot again.")

            if self.proxy is not None:
                if self.proxy.monitor is not None:
                    self.proxy.terminate()
                    logger.info("Proxy terminated")
                    self.proxy.monitor = None
                    self.monitor_scheduler.resume()
                    logger.info("Resumed DropBot monitor")

    def on_retry_connection_request(self, message):
        logger.info("Attempting to retry connecting with a dropbot")
        self.monitor_scheduler.resume()

    def on_halted_request(self, message):
        self._no_power = True
        self.proxy.terminate()
        self.proxy.monitor = None
        logger.error("Halted DropBot: Disconnect everything and reconnect")

    ################################# Protected methods ######################################
    def _on_dropbot_port_found(self, event):
        """
        Method defining what to do when dropbot has been found on a port.
        """
        logger.debug("DropBot port found")
        self.monitor_scheduler.pause()
        logger.debug("Paused DropBot monitor")
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
        self._no_power = False
        err = None

        if self.proxy is None or getattr(self, 'proxy.monitor', None) is None:

            logger.debug("Dropbot not connected. Attempting to connect")

            ############################### Attempt to make a proxy object #############################

            try:
                logger.debug(f"Attempting to create DropBot serial proxy on port {port_name}")
                self.proxy = DramatiqDropbotSerialProxy(port=port_name)
                # this will send out a connected signal to the message router is successful

            except (IOError, AttributeError) as e:
                publish_message(topic=NO_DROPBOT_AVAILABLE, message=str(e))
                err = e

            except dropbot.proxy.NoPower as e:
                self._no_power = True
                publish_message(topic=NO_POWER, message=str(e))
                err = e

            except Exception as e:
                err = e

            else:
            ################################# Post connection steps ###################################
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

            ###########################################################################################

            finally:
                if err:
                    logger.error(err)

        # if the dropbot is already connected
        else:
            logger.info("Dropbot already connected on port %s", port_name)

    def _setup_dropbot(self):
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

    def _capacitance_updated_wrapper(self, signal: dict[str, str]):
        capacitance = float(signal['new_value']) * self.ureg.farad
        capacitance_formatted = f"{capacitance.to(self.ureg.picofarad):.2g~P}"
        voltage = float(signal['V_a']) * self.ureg.volt
        voltage_formatted = f"{voltage:.2g~P}"
        publish_message(topic=CAPACITANCE_UPDATED,
                        message=json.dumps({'capacitance': capacitance_formatted, 'voltage': voltage_formatted}))

    @staticmethod
    def _halted_event_wrapper():
        publish_message(topic=HALTED, message='DropBot halted')

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
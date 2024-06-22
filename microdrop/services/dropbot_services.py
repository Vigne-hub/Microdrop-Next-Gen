import functools
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
from microdrop.plugins.frontend_plugins.dropbot_GUI import DropBotControlWidget
from microdrop.pydantic_models.dropbot_controller_signals import DBVoltageChangedModel, \
    DBChannelsMetastateChanged, DBChannelsChangedModel, DBConnectionStateModel, \
    DBChipInsertStateModel, DBErrorModel
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message, MessageRouterActor
from microdrop_utils._logger import get_logger
from microdrop_utils.pub_sub_serial_proxy import DropbotSerialProxy

logger = get_logger(__name__)


def check_connected_ports_hwid(id_to_screen, regexp='USB Serial'):
    """Check connected USB ports for a list of valid ports"""
    logger.info(f'attempting to find valid ports')
    connected_ports = grep(regexp)
    valid_ports = []

    for port in connected_ports:
        pattern = re.compile(f".*{id_to_screen}.*")
        teensy = re.search(pattern, port.hwid)
        if bool(teensy):
            valid_ports.append(port)

    logger.info(f'Valid ports found: {valid_ports}')
    return valid_ports


def check_dropbot_devices_available(hwids_to_check):
    """Method to find dropbots avaliable and which ports it make be connected to"""
    try:
        logger.info(f'Checking to see if there exists a DropBot device available')
        for hwid in hwids_to_check:
            valid_ports = check_connected_ports_hwid(hwid)
            if valid_ports:
                port_name = str(valid_ports[0].name)
                logger.info(f'DropBot found on port {port_name}')
                return port_name
    except Exception as e:
        logger.error(f'No DropBot available for connection with exception {e}: dropbot/error')
        return None


@provides(IDropbotControllerService)
class DropbotService(HasTraits):
    dropbot_connected = DBConnectionStateModel(Signal='dropbot_connected', Connected=True)
    dropbot_disconnected = DBConnectionStateModel(Signal='dropbot_connected', Connected=False)
    chip_inserted = DBChipInsertStateModel(Signal='chip_inserted', ChipInserted=True)
    chip_not_inserted = DBChipInsertStateModel(Signal='chip_inserted', ChipInserted=False)
    db_error_no_power = DBErrorModel(Signal='dropbot_warning', Error='No power to DropBot')
    db_error_no_db_available = DBErrorModel(Signal='dropbot_warning', Error='No DropBot available for connection')

    def __init__(self):
        logger.info('Initializing dropbot services')

        self.make_serial_proxy = self._make_serial_proxy()
        self.ui_listener = self.create_dropbot_backend_listener_actor()

        # actor_topics

        self.actor_topics_dict = {"dropbot_backend_listener": ["dropbot/signals/+"],
                                  ""
                                  }

        self.proxy: Union[DropbotSerialProxy, None] = None

        hwids_to_check = ["VID:PID=16C0:"]

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=1),
        )
        scheduler.add_listener(self.on_dropbot_port_found, EVENT_JOB_EXECUTED)
        self.scheduler = scheduler
        self.scheduler.start()

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

    def on_connected(self):
        self.scheduler.pause()

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
                self.emit_signal(self.db_error_no_db_available)
                logger.error("No DropBot available for connection")
            except dropbot.proxy.NoPower:
                self.emit_signal(self.db_error_no_power)
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
            logger.info(f"UI_LISTENER: Received message: {message} from topic: {topic}")

            topic = topic.split("/")

            if topic[-1] == "connected":
                self.on_connected()

            if topic[-1] == "disconnected":
                if self.proxy.monitor is not None:
                    self.proxy.terminate()
                    self.proxy.monitor = None
                    self.on_disconnected()

        return dropbot_backend_listener


    def setup_dropbot(self):
        OUTPUT_ENABLE_PIN = 22
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            self.emit_signal(self.chip_not_inserted)
        else:
            self.emit_signal(self.chip_inserted)
        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        if signal['event'] == 'output_enabled':
            self.emit_signal(self.chip_inserted)
        elif signal['event'] == 'output_disabled':
            self.emit_signal(self.chip_not_inserted)
        else:
            logger.warn(f"Unknown signal received: {signal}")


def main():
    app = QApplication(sys.argv)
    router_actor = MessageRouterActor()

    dropbot_status = DropBotControlWidget()
    dropbot_status.show()
    dropbot_services = DropbotService()


if __name__ == "__main__":

    BROKER = get_broker()

    for el in BROKER.middleware:
        if el.__module__ == "dramatiq.middleware.prometheus":
            BROKER.middleware.remove(el)

    worker = Worker(broker=BROKER)

    try:
        BROKER.flush_all()
        worker.start()
        main()

    except KeyboardInterrupt or SystemExit:
        worker.stop()
        BROKER.flush_all()
        BROKER.close()
        sys.exit(0)

    finally:
        worker.stop()
        BROKER.flush_all()
        BROKER.close()
        sys.exit(0)

import functools

from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from traits.api import HasTraits, provides
from PySide6.QtCore import QTimer

from ..interfaces.i_dropbot_controller_service import IDropbotControllerService
from ..pydantic_models.dropbot_controller_signals import DBOutputStateModel, \
    DBChannelsChangedModel, DBVoltageChangedModel, DBChannelsMetastateChanged

import dramatiq
from microdrop_utils.dramatiq_pub_sub_helpers import publish_message

from typing import Union
import dropbot
from dropbot.monitor import DROPBOT_SIGNAL_NAMES
import serial
import sys
import numpy as np
from nptyping import NDArray, Shape, UInt8

from microdrop_utils._logger import get_logger

logger = get_logger(__name__)

to_delete = []
for m in sys.modules:
    if any(x in m for x in ['work', 'google3']):
        to_delete.append(m)

for m in to_delete:
    del sys.modules[m]


@provides(IDropbotControllerService)
class DropbotService(HasTraits):
    output_state_true = DBOutputStateModel(Signal='output_state_changed', OutputState=True)
    output_state_false = DBOutputStateModel(Signal='output_state_changed', OutputState=False)

    def __init__(self):
        """
        Initializes the DropbotController instance and sets up timers for
        Dropbot initialization and voltage polling.

        Args:
            parent (QObject, optional): The parent QObject. Defaults to None.
        """
        super().__init__()
        self.proxy: DropbotSerialProxy = None
        self.port_name = None
        self.dropbot_job_submitted = False
        scheduler = BackgroundScheduler()
        self.dropbot_search_submitted = False
        hwids_to_check = ["VID:PID=16C0:"]
        scheduler.add_job(
            func=functools.partial(check_dropbot_devices_available, hwids_to_check),
            trigger=IntervalTrigger(seconds=1),
        )

        # Add listeners to handle job events
        scheduler.add_listener(self.on_dropbot_port_found, EVENT_JOB_EXECUTED)

        self.scheduler = scheduler

        self.ui_listener = self.create_ui_listener_actor()
        self.make_serial_proxy = self._make_serial_proxy()

        self.actor_topics_dict = {"ui_listener_actor": ["dropbot/signals/+"]}

        self.last_state: NDArray[Shape['*, 1'], UInt8] = np.zeros(128, dtype='uint8')

    def connect_signals(self):
        self.proxy.signals.signal('connected').connect(self.connected)
        self.proxy.signals.signal('disconnected').connect(self.disconnected)
        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed)
        self.proxy.signals.signal('capacitance_updated').connect(self.capacitance_updated)
        self.proxy.signals.signal('channels_updated').connect(self.channels_updated)
        self.proxy.signals.signal('shorts_detected').connect(self.shorts_detected)

    def emit_signal(self, message):
        publish_message(message, f'dropbot_controller/{message.Signal}')  #assume message is already in json format
        logger.info(f"Emitted: {message}")

    def init_dropbot_proxy(self):
        """
        Attempts to establish a serial connection with the Dropbot and configure
        initial settings. Stops the initialization timer on success and starts
        the voltage polling timer.
        """
        try:
            port = serial.serial_for_url('hwgrep://USB Serial', do_not_open=True).port
            self.proxy = dropbot.SerialProxy(port=port)
        except (IOError, AttributeError):  # No dropbot connected
            self.proxy = None
            return

        self.connect_signals()
        # Stop timer
        self.dropbot_timer.stop()
        self.dropbot_timer.timeout.disconnect(self.init_dropbot_proxy)
        self.dropbot_timer.timeout.connect(self.poll_voltage)
        self.dropbot_timer.start(1000)

        # Fetch initial state
        self.proxy.hv_output_enabled = False
        self.proxy.voltage = 0
        self.proxy.frequency = 10000
        self.last_state = np.array(self.proxy.state_of_channels)
        self.last_state = self.get_channels()

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed)

        OUTPUT_ENABLE_PIN = 22
        # Chip may have been inserted before connecting, so `chip-inserted`
        # event may have been missed.
        # Explicitly check if chip is inserted by reading **active low**
        # `OUTPUT_ENABLE_PIN`.
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            self.emit_signal(self.output_state_false)
        else:
            self.emit_signal(self.output_state_true)

    def output_state_changed(self, signal: dict[str, str]):
        """
        Processes the signals related to the output state (enabled/disabled) and
        emits the corresponding Qt signals.

        Args:
            signal (dict[str, str]): The signal data containing the event type.
        """
        if signal['event'] == 'output_enabled':
            self.emit_signal(self.output_state_true)
        elif signal['event'] == 'output_disabled':
            self.emit_signal(self.output_state_false)
        else:
            raise ValueError("Unknown signal received")

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

    #####SIGNAL HANDLERS######

    @dramatiq.actor
    def shorts_detected(self, sender, **kwargs):
        # Handle shorts detection, depending on application specifics
        shorts_info = kwargs.get('info')
        self.emit_signal({'Signal': 'shorts_detected', 'Info': shorts_info})

    @dramatiq.actor
    def channels_updated(self, sender, **kwargs):
        # Handle channels updates, depending on application specifics
        channels = kwargs.get('channels')
        self.emit_signal(DBChannelsChangedModel(Signal='channels_changed', channels=str(channels)))

    @dramatiq.actor
    def capacitance_updated(self, sender, **kwargs):
        # Handle capacitance updates, depending on application specifics
        capacitance = kwargs.get('capacitance')
        self.emit_signal({'Signal': 'capacitance_updated', 'Capacitance': capacitance})

    @dramatiq.actor
    def output_state_changed(self, sender, **kwargs):
        if kwargs.get('event') == 'output_enabled':
            self.emit_signal(DBOutputStateModel(Signal='output_state_changed', OutputState=True))
        elif kwargs.get('event') == 'output_disabled':
            self.emit_signal(DBOutputStateModel(Signal='output_state_changed', OutputState=False))

    @dramatiq.actor
    def connected(self, sender, **kwargs):
        self.emit_signal({'Signal': 'connected', 'Message': 'DropBot connected.'})

    @dramatiq.actor
    def disconnected(self, sender, **kwargs):
        self.emit_signal({'Signal': 'disconnected', 'Message': 'DropBot disconnected.'})


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    service = DropbotService()
    sys.exit(app.exec())

from PySide6.QtCore import QTimer
import logging

from traits.api import HasTraits, provides, Union, Instance, Array
from microdrop.interfaces.i_dropbot_controller_service import IDropbotControllerService

from microdrop.pydantic_models.dropbot_controller_output_state_model import DBOutputStateModel, \
    DBChannelsChangedModel, DBVoltageChangedModel, DBChannelsMetastateChanged

logger = logging.getLogger(__name__)

import dropbot
from dropbot.monitor import DROPBOT_SIGNAL_NAMES
import serial
import sys

to_delete = []
for m in sys.modules:
    if any(x in m for x in ['work', 'google3']):
        to_delete.append(m)

for m in to_delete:
    del sys.modules[m]

import numpy as np


@provides(IDropbotControllerService)
class DropbotControllerService(HasTraits):
    # init traits

    proxy = Union(None, Instance(dropbot.SerialProxy))
    last_state = Array(dtype=np.uint8, shape=(None, 1))
    dropbot_timer = Instance(QTimer)

    # set default values for traits
    def _last_state_default(self):
        return np.zeros(128, dtype=np.uint8)

    def _proxy_default(self):
        return None

    def _dropbot_timer_default(self):
        timer = QTimer()
        timer.timeout.connect(self.init_dropbot_proxy)
        timer.start(1000)
        return timer

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

        # self.proxy.

        # Connect signals
        # for signal in DROPBOT_SIGNAL_NAMES:
        #     logger.info("Connecting to signal %s", signal)
        #     self.proxy.signals.signal(signal).connect(self.signal_wrapper)

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed)

        # self.dropbot_signal.connect(self.log_signal)

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

    # def signal_wrapper(self, signal):
    #     self.dropbot_signal.emit(signal)

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

    def set_voltage(self, voltage: int):
        """
        Sets the voltage of the Dropbot to the specified value.

        Args:
            voltage (int): Desired voltage setting.
        """
        logging.debug(f"Setting voltage to {voltage}")
        if self.proxy is not None:
            self.proxy.voltage = voltage
        logger.info("Voltage set to %d", voltage)

    def set_frequency(self, frequency: int):
        """
        Sets the frequency of the Dropbot to the specified value.

        Args:
            frequency (int): Desired frequency setting.
        """
        logging.debug(f"Setting frequency to {frequency}")
        if self.proxy is not None:
            self.proxy.frequency = frequency
        logger.info("Frequency set to %d", frequency)

    def set_hv(self, on: bool):
        """
        Enables or disables the high voltage output of the Dropbot.

        Args:
            on (bool): True to enable high voltage, False to disable.
        """
        if self.proxy is not None:
            self.proxy.hv_output_enabled = on

    def get_channels(self) -> Array(dtype=np.uint8, shape=(None, 1)):
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

    def set_channels(self, channels: Array(dtype=np.uint8, shape=(None, 1))):
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

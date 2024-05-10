

logger = initialize_logger(__name__)

from typing import Union, Callable
from functools import partial

from PySide6.QtCore import QObject, Signal, SignalInstance, QTimer

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
from nptyping import NDArray, Shape, UInt8


# def co_connect(name):
#     def _wrapped(sender, **message):
#         async def co_callback(message_):
#             signal = signals_.get(name)
#             if signal:
#                 await signal.send('keep_alive', **message_)
#             # await asyncio.gather(*(listener[1] for listener in listeners))
#
#         return loop.call_soon_threadsafe(loop.create_task, co_callback(sender, **message))
#
#     return _wrapped

class DropbotController(QObject):
    channels_changed: SignalInstance = Signal(object)
    channels_metastate_changed: SignalInstance = Signal(object)
    output_state_changed: SignalInstance = Signal(bool)
    dropbot_signal: SignalInstance = Signal(object)
    voltage_changed: SignalInstance = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.proxy: Union[None, dropbot.SerialProxy] = None
        self.last_state: NDArray[Shape['*, 1'], UInt8] = np.zeros(128, dtype='uint8')

        # self.init_dropbot_proxy()

        self.dropbot_timer = QTimer()
        self.dropbot_timer.timeout.connect(self.init_dropbot_proxy)
        self.dropbot_timer.start(1000)

    def init_dropbot_proxy(self):
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

        self.proxy.signals.signal('output_enabled').connect(self.output_state_changed_wrapper)
        self.proxy.signals.signal('output_disabled').connect(self.output_state_changed_wrapper)

        # self.dropbot_signal.connect(self.log_signal)

        OUTPUT_ENABLE_PIN = 22
        # Chip may have been inserted before connecting, so `chip-inserted`
        # event may have been missed.
        # Explicitly check if chip is inserted by reading **active low**
        # `OUTPUT_ENABLE_PIN`.
        if self.proxy.digital_read(OUTPUT_ENABLE_PIN):
            self.output_state_changed.emit(False)
        else:
            self.output_state_changed.emit(True)

    def output_state_changed_wrapper(self, signal: dict[str, str]) -> Callable:
        if signal['event'] == 'output_enabled':
            self.output_state_changed.emit(True)
        elif signal['event'] == 'output_disabled':
            self.output_state_changed.emit(False)
        else:
            logger.warning("Unknown signal received: %s", signal)

    # def signal_wrapper(self, signal):
    #     self.dropbot_signal.emit(signal)

    def poll_voltage(self):
        if self.proxy is not None:
            try:
                voltage = self.proxy.high_voltage()
                self.voltage_changed.emit(voltage)
            except OSError:  # No dropbot connected
                pass

    def set_voltage(self, voltage: int):
        if self.proxy is not None:
            self.proxy.voltage = voltage
        logger.info("Voltage set to %d", voltage)

    def set_frequency(self, frequency: int):
        if self.proxy is not None:
            self.proxy.frequency = frequency
        logger.info("Frequency set to %d", frequency)

    def set_hv(self, on: bool):
        if self.proxy is not None:
            self.proxy.hv_output_enabled = on

    def get_channels(self) -> NDArray[Shape['*, 1'], UInt8]:
        if self.proxy is None:
            return np.zeros(128, dtype='uint8')

        channels = np.array(self.proxy.state_of_channels)
        if (self.last_state != channels).any():
            self.last_state = channels
            self.channels_changed.emit(channels)
        return channels

    def set_channels(self, channels: NDArray[Shape['*, 1'], UInt8]):
        if self.proxy is None:
            return
        self.proxy.state_of_channels = np.array(channels)
        self.last_state = self.get_channels()

    def set_channel_single(self, channel: int, state: bool):
        if self.proxy is None:
            return
        channels = self.get_channels()
        channels[channel] = state
        self.set_channels(channels)

    def droplet_search(self, threshold: float = 0):
        if self.proxy is not None:
            # Disable all electrodes
            self.set_channels(np.zeros_like(self.last_state))

            drops = list(self.last_state)
            for drop in self.proxy.get_drops(capacitance_threshold=threshold):
                for electrode in drop:
                    drops[electrode] = 'droplet'

            self.channels_metastate_changed.emit(drops)

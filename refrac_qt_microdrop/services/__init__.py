from traits.api import HasTraits, Float, Bool, Array, Event, provides
from refrac_qt_microdrop.interfaces import IVoltageService, IOutputService, IChannelService
import numpy as np
from nptyping import NDArray, Shape, UInt8
import dropbot
import serial

@provides(IVoltageService)
class VoltageService(HasTraits):
    voltage_changed = Event(Float)
    proxy: dropbot.SerialProxy = None

    def set_voltage(self, voltage: int):
        if self.proxy is not None:
            self.proxy.voltage = voltage

    def get_voltage(self) -> float:
        if self.proxy is not None:
            return self.proxy.high_voltage()
        return 0.0

@provides(IOutputService)
class OutputService(HasTraits):
    output_state_changed = Event(Bool)
    proxy: dropbot.SerialProxy = None

    def set_output(self, on: bool):
        if self.proxy is not None:
            self.proxy.hv_output_enabled = on

@provides(IChannelService)
class ChannelService(HasTraits):
    channels_changed = Event(Array)
    proxy: dropbot.SerialProxy = None
    last_state: NDArray[Shape['*, 1'], UInt8] = np.zeros(128, dtype='uint8')

    def set_channel_single(self, channel: int, state: bool):
        if self.proxy is None:
            return
        channels = self.get_channels()
        channels[channel] = state
        self.set_channels(channels)

    def get_channels(self) -> NDArray[Shape['*, 1'], UInt8]:
        if self.proxy is None:
            return np.zeros(128, dtype='uint8')
        channels = np.array(self.proxy.state_of_channels)
        if (self.last_state != channels).any():
            self.last_state = channels
            self.channels_changed = channels
        return channels

    def set_channels(self, channels: NDArray[Shape['*, 1'], UInt8]):
        if self.proxy is None:
            return
        self.proxy.state_of_channels = np.array(channels)
        self.last_state = self.get_channels()

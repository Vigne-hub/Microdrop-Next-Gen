# interfaces.py

from traits.api import Interface, Float, Bool, Array, Event


class IVoltageService(Interface):
    voltage_changed = Event(Float)

    def set_voltage(self, voltage: int):
        pass

    def get_voltage(self) -> float:
        pass


class IOutputService(Interface):
    output_state_changed = Event(Bool)

    def set_output(self, on: bool):
        pass


class IChannelService(Interface):
    channels_changed = Event(Array)

    def set_channel_single(self, channel: int, state: bool):
        pass

    def get_channels(self) -> Array:
        pass

from __future__ import annotations

from typing import Union, Sequence

from PySide6.QtCore import QObject, SignalInstance, Signal
from nptyping import NDArray, Shape, Float, UInt8

from .dmf_utils import ElectrodeDict
from envisage_sample.widgets import initialize_logger

logger = initialize_logger(__name__)


class Electrode(QObject):
    state_changed = Signal(int, bool)
    metastate_changed = Signal(int, object)

    @classmethod
    def from_dict(cls, d: ElectrodeDict, parent=None):
        return cls(d['channel'], d['path'], parent=parent)

    def __init__(self, channel: int, path: NDArray[Shape['*, 1, 1'], Float], parent=None):
        super().__init__(parent=parent)
        self.channel = channel  #electrode id
        self.path = path  #NDArray path to electrode
        self._state = False
        self._metastate = None

        logger.debug("Electrode %s created", self.channel)  # on test loaded 93 electrodes

    def get_state(self) -> bool:
        return self._state

    def set_state(self, state: bool):
        if state != self._state and self.channel is not None:  # Only emit signal if state has changed
            self._state = state
            self.state_changed.emit(self.channel, self._state)
            logger.debug("State changed to %s for %s", self.get_state(), self.channel)

    def get_metastate(self) -> object:
        return self._metastate

    def set_metastate(self, metastate: object):
        if metastate != self._metastate:
            self._metastate = metastate
            self.metastate_changed.emit(self.channel, self.get_metastate())

    def toggle_state(self):
        logger.debug("State changed to %s for %s", not self.get_state(), self.channel)
        self.set_state(not self.get_state())  # Correct way to toggle state


class Electrodes(QObject):
    electrode_state_changed: SignalInstance = Signal(int, bool)

    def __init__(self, electrodes: dict[str, Electrode] = None, parent=None):
        super().__init__(parent=parent)
        if electrodes:
            self.electrodes = electrodes
        else:
            self.electrodes: dict[str, Electrode] = {}

    def __getitem__(self, item: str) -> Electrode:
        return self.electrodes[item]

    def __setitem__(self, key, value):
        self.electrodes[key] = value
        self.electrodes[key].state_changed.connect(self.electrode_state_changed)

    def values(self):
        return self.electrodes.values()

    def keys(self):
        return self.electrodes.keys()

    def items(self):
        return self.electrodes.items()

    def set_electrodes(self, electrodes: dict[str, Electrode]):
        for e in self.electrodes.values():
            e.state_changed.disconnect(self.electrode_state_changed)
        self.electrodes = electrodes
        for v in self.electrodes.values():
            v.state_changed.connect(self.electrode_state_changed)

    def toggle_all_electrodes_off(self):
        for e in self.electrodes.values():
            e.set_state(False)

    def toggle_on_batch(self, electrodes):
        logger.debug("Attempt to toggling on batch electrodes: %s", electrodes)
        for e in self.electrodes.keys():
            if e in electrodes:
                self.electrodes[e].set_state(True)

    def sync_electrode_states(self, states: Sequence[str | int]):
        for k, v in self.electrodes.items():
            try:
                v.state = states[v.channel]
            except KeyError:
                logger.warning(f"Channel {v.channel} not found in states")

    def sync_electrode_metastates(self, metastates: Sequence[str | int]):
        for k, v in self.electrodes.items():
            try:
                v.metastate = metastates[v.channel]
            except KeyError:
                logger.warning(f"Channel {v.channel} not found in metastates")

    def check_electrode_range(self, n_channels: int) -> list[str]:
        """
        Checks that the electrode channel numbers are within n_channels
        :param n_channels: number of channels present
        :return: list of electrode names that are out of range
        """
        return [k for k, v in self.electrodes.items() if v.channel >= n_channels]

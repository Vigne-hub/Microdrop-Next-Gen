from __future__ import annotations
from typing import Sequence
from envisage_sample.widgets import initialize_logger

from traits.api import HasTraits, Int, Bool, Array, Float, Any

logger = initialize_logger(__name__)


class Electrode(HasTraits):
    """
    Electrode class for managing individual electrodes
    """

    #: Channel number
    channel = Int()

    #: NDArray path to electrode
    path = Array(dtype=Float, shape=(None, 1, 2))

    #: State of the electrode (On or Off)
    _state = Bool(False)

    #: Metastates of the electrode (Droplet in or not for example and other properties)
    _metastate = Any()

    @property
    def state(self) -> bool:
        return self._state

    @state.setter
    def state(self, state: bool):
        if state != self._state and self.channel is not None:
            self._state = state
            logger.debug("State changed to %s for %s", self.state, self.channel)

    @property
    def metastate(self) -> object:
        return self._metastate

    @metastate.setter
    def metastate(self, metastate: object):
        if metastate != self._metastate:
            self._metastate = metastate


class Electrodes:  # QObject

    """
    Electrodes class for managing multiple electrodes
    """

    def __init__(self, electrodes: dict[str, Electrode] = None):

        if electrodes:
            self._electrodes = electrodes
        else:
            self._electrodes: dict[str, Electrode] = {}

    @property
    def electrodes(self) -> dict[str, Electrode]:
        return self._electrodes

    @electrodes.setter
    def electrodes(self, electrodes: dict[str, Electrode]):
        self._electrodes = electrodes

    def __getitem__(self, item: str) -> Electrode:
        return self._electrodes[item]

    def __setitem__(self, key, value):
        self._electrodes[key] = value

    def values(self):
        return self._electrodes.values()

    def keys(self):
        return self._electrodes.keys()

    def items(self):
        return self._electrodes.items()

    def sync_electrode_states(self, states: Sequence[str | int]):
        for k, v in self.items():
            try:
                v.state = states[v.channel]
            except KeyError:
                logger.warning(f"Channel {v.channel} not found in states")

    def sync_electrode_metastates(self, metastates: Sequence[str | int]):
        for k, v in self.items():
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
        return [k for k, v in self.items() if v.channel >= n_channels]

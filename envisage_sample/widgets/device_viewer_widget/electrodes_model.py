from .. import initialize_logger

from traits.api import HasTraits, Int, Bool, Array, Float, Any, Dict, Str, List, Property

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

    #: Property for state
    state = Property(Bool, depends_on='_state')

    #: Property for metastate
    metastate = Property(Any, depends_on='_metastate')

    def _get_state(self) -> Bool:
        return self._state

    def _set_state(self, state: Bool):
        if state != self._state and self.channel is not None:
            self._state = state
            logger.debug("State changed to %s for %s", self.state, self.channel)

    def _get_metastate(self) -> object:
        return self._metastate

    def _set_metastate(self, metastate: object):
        if metastate != self._metastate:
            self._metastate = metastate


class Electrodes(HasTraits):  # QObject

    """
    Electrodes class for managing multiple electrodes
    """

    #: "Dictionary of electrodes with keys being an electrode id and values being the electrode object"
    _electrodes = Dict(Str, Electrode, desc="Dictionary of electrodes with keys being an electrode id and values "
                                            "being the electrode object")

    electrodes = Property(Dict(Str, Electrode), depends_on='_electrodes')

    def _get_electrodes(self) -> Dict(Str, Electrode):
        return self._electrodes

    def _set_electrodes(self, electrodes: Dict(Str, Electrode)):
        self._electrodes = electrodes

    def __getitem__(self, item: Str) -> Electrode:
        return self._electrodes[item]

    def __setitem__(self, key, value):
        self._electrodes[key] = value

    def values(self):
        return self._electrodes.values()

    def keys(self):
        return self._electrodes.keys()

    def items(self):
        return self._electrodes.items()

    def sync_electrode_states(self, states: Array(Str or Int)):
        for k, v in self.items():
            try:
                v.state = states[v.channel]
            except KeyError:
                logger.warning(f"Channel {v.channel} not found in states")

    def sync_electrode_metastates(self, metastates: Array(Str or Int)):
        for k, v in self.items():
            try:
                v.metastate = metastates[v.channel]
            except KeyError:
                logger.warning(f"Channel {v.channel} not found in metastates")

    def check_electrode_range(self, n_channels: Int) -> List(Str):
        """
        Checks that the electrode channel numbers are within n_channels
        :param n_channels: number of channels present
        :return: list of electrode names that are out of range
        """
        return [k for k, v in self.items() if v.channel >= n_channels]

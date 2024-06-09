# Imports:

# local
from ..utils.dmf_utils import SvgUtil
from _logger import get_logger

# enthought
from traits.api import HasTraits, Int, Bool, Array, Float, Any, Dict, Str, Instance, Property, File

logger = get_logger(__name__)


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


class Electrodes(HasTraits):

    """
    Electrodes class for managing multiple electrodes
    """

    #: "Dictionary of electrodes with keys being an electrode id and values being the electrode object"
    _electrodes = Dict(Str, Electrode, desc="Dictionary of electrodes with keys being an electrode id and values "
                                            "being the electrode object")

    electrodes = Property(Dict(Str, Electrode), depends_on='_electrodes')

    svg_model = Instance(SvgUtil, allow_none=True, desc="Model for the SVG file if given")

    # -------------------Magic methods ----------------------------------------------------------------------
    def __getitem__(self, item: Str) -> Electrode:
        return self._electrodes[item]

    def __setitem__(self, key, value):
        self._electrodes[key] = value

    # -------------------Trait Property getters and setters --------------------------------------------------
    def _get_electrodes(self) -> Dict(Str, Electrode):
        return self._electrodes

    def _set_electrodes(self, electrodes: Dict(Str, Electrode)):
        self._electrodes = electrodes

    # -------------------Trait change handlers --------------------------------------------------
    def _svg_model_changed(self, new_model: SvgUtil):
        for k, v in new_model.electrodes.items():
            self.electrodes[k] = Electrode(channel=v['channel'], path=v['path'])

        logger.debug(f"Created electrodes from SVG file: {new_model.filename}")

    # -------------------Public methods --------------------------------------------------
    def set_electrodes_from_svg_file(self, svg_file: File):
        """
        Get electrodes from SVG file
        :param svg_file: Path to SVG file
        :return: Dictionary of electrodes
        """

        self.svg_model = SvgUtil(svg_file)
        logger.debug(f"Setting electrodes from SVG file: {svg_file}")

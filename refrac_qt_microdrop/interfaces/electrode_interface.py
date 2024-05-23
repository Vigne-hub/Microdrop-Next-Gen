# interfaces/electrode_interface.py
from traits.api import Interface

class IElectrodeControllerService(Interface):

    def toggle_state(self, channel: int):
        pass

    def set_state(self, channel: int, state: bool):
        pass

    def get_state(self, channel: int) -> bool:
        pass

    def set_metastate(self, channel: int, metastate: object):
        pass

    def get_metastate(self, channel: int) -> object:
        pass

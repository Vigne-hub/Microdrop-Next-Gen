# interfaces/electrode_interface.py
from traits.api import Interface

class IElectrodeControllerService(Interface):

    def toggle_all_electrodes_off(self):
        pass

    def toggle_on_batch(self, electrodes):
        pass

    def sync_electrode_states(self, states):
        pass

    def sync_electrode_metastates(self, metastates):
        pass

    def check_electrode_range(self, n_channels):
        pass

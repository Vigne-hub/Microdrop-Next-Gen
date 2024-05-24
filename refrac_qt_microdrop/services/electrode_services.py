# services/electrode_service.py
from traits.api import HasTraits, provides
from refrac_qt_microdrop.interfaces.electrode_interface import IElectrodeControllerService
from refrac_qt_microdrop.helpers.logger import initialize_logger
from refrac_qt_microdrop.backend_plugins.electrode_plugin import ElectrodeActor

logger = initialize_logger(__name__)

@provides(IElectrodeControllerService)
class ElectrodeService(HasTraits):
    electrode_actor = ElectrodeActor()

    def toggle_all_electrodes_off(self):
        logger.debug("Sending toggle_all_electrodes_off command to queue")
        self.electrode_actor.process_task.send({"name": "toggle_all_electrodes_off", "args": [], "kwargs": {}})

    def toggle_on_batch(self, electrodes):
        logger.debug("Sending toggle_on_batch command to queue with electrodes: %s", electrodes)
        self.electrode_actor.process_task.send({"name": "toggle_on_batch", "args": [electrodes], "kwargs": {}})

    def sync_electrode_states(self, states):
        logger.debug("Sending sync_electrode_states command to queue with states: %s", states)
        self.electrode_actor.process_task.send({"name": "sync_electrode_states", "args": [states], "kwargs": {}})

    def sync_electrode_metastates(self, metastates):
        logger.debug("Sending sync_electrode_metastates command to queue with metastates: %s", metastates)
        self.electrode_actor.process_task.send({"name": "sync_electrode_metastates", "args": [metastates], "kwargs": {}})

    def check_electrode_range(self, n_channels):
        logger.debug("Sending check_electrode_range command to queue with n_channels: %s", n_channels)
        self.electrode_actor.process_task.send({"name": "check_electrode_range", "args": [n_channels], "kwargs": {}})

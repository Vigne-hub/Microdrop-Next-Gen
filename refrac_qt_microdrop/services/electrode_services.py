# services/electrode_service.py
from traits.api import HasTraits, provides
from refrac_qt_microdrop.interfaces.electrode_interface import IElectrodeControllerService
from refrac_qt_microdrop.helpers.logger import initialize_logger
from refrac_qt_microdrop.backend_plugins.electrode_plugin import ElectrodeActor

logger = initialize_logger(__name__)

@provides(IElectrodeControllerService)
class ElectrodeService(HasTraits):
    electrode_actor = ElectrodeActor()

    def toggle_state(self, channel: int):
        logger.debug(f"Attempting to send toggle_state command to queue for channel {channel}")
        self.electrode_actor.process_task.send({"name": "toggle_state", "args": [channel], "kwargs": {}})

    def set_state(self, channel: int, state: bool):
        logger.debug(f"Attempting to send set_state command to queue for channel {channel} with state {state}")
        self.electrode_actor.process_task.send({"name": "set_state", "args": [channel, state], "kwargs": {}})

    def get_state(self, channel: int) -> bool:
        logger.debug(f"Attempting to send get_state command to queue for channel {channel}")
        return self.electrode_actor.process_task.send_with_options(
            {"name": "get_state", "args": [channel], "kwargs": {}},
            block=True,
            result_returning=True,
        ).result()

    def set_metastate(self, channel: int, metastate: object):
        logger.debug(f"Attempting to send set_metastate command to queue for channel {channel} with metastate {metastate}")
        self.electrode_actor.process_task.send({"name": "set_metastate", "args": [channel, metastate], "kwargs": {}})

    def get_metastate(self, channel: int) -> object:
        logger.debug(f"Attempting to send get_metastate command to queue for channel {channel}")
        return self.electrode_actor.process_task.send_with_options(
            {"name": "get_metastate", "args": [channel], "kwargs": {}},
            block=True,
            result_returning=True,
        ).result()

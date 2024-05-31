from traits.api import HasTraits, provides
from refrac_qt_microdrop.interfaces.dropbot_interface import IDropbotControllerService
from refrac_qt_microdrop.backend_logic.dropbot_controller import DropbotController
from refrac_qt_microdrop.backend_plugins.dropbot_controller import DropbotActor
from refrac_qt_microdrop.helpers.logger import initialize_logger

logger = initialize_logger(__name__)


@provides(IDropbotControllerService)
class DropbotService(HasTraits):
    dropbot_actor = DropbotActor()

    def poll_voltage(self):
        logger.debug("Attempting to send poll_voltage command to queue")
        self.dropbot_actor.process_task.send({"name": "poll_voltage",
                                              "args": [],
                                              "kwargs": {}})

    def set_voltage(self, voltage: int):
        logger.debug("Attempting to send set_voltage command to queue")
        self.dropbot_actor.process_task.send({"name": "set_voltage",
                                              "args": [voltage],
                                              "kwargs": {}})

    def set_frequency(self, frequency: int):
        logger.debug("Attempting to send set_frequency command to queue with frequency: %s" % frequency)
        self.dropbot_actor.process_task.send({"name": "set_frequency",
                                              "args": [frequency],
                                              "kwargs": {}})

    def set_hv(self, on: bool):
        logger.debug("Attempting to send set_hv command to queue with state: %s" % on)
        self.dropbot_actor.process_task.send({"name": "set_hv",
                                              "args": [on],
                                              "kwargs": {}})

    def get_channels(self):
        logger.debug("Attempting to send get_channels command to queue")
        self.dropbot_actor.process_task.send({"name": "get_channels",
                                              "args": [],
                                              "kwargs": {}})

    def set_channels(self, channels):
        logger.debug("Attempting to send set_channels command to queue with channels: %s" % channels)
        self.dropbot_actor.process_task.send({"name": "set_channels",
                                              "args": [channels],
                                              "kwargs": {}})

    def set_channel_single(self, channel: int, state: bool):
        logger.debug("Attempting to send set_channel_single command to queue with channel: %s and state: %s" % (channel, state))
        self.dropbot_actor.process_task.send({"name": "set_channel_single",
                                              "args": [channel, state],
                                              "kwargs": {}})

    def droplet_search(self, threshold: float = 0):
        logger.debug("Attempting to send droplet_search command to queue with threshold: %s" % threshold)
        self.dropbot_actor.process_task.send({"name": "droplet_search",
                                              "args": [threshold],
                                              "kwargs": {}})

from traits.api import HasTraits, provides
from refrac_qt_microdrop.interfaces import IDropbotControllerService
from refrac_qt_microdrop.helpers.dropbot_controller_helper import DropbotController
from refrac_qt_microdrop.backend_plugins.dropbot_controller import DropbotActor


@provides(IDropbotControllerService)
class DropbotService(HasTraits):
    controller = DropbotController()
    dropbot_actor = DropbotActor()

    def poll_voltage(self):
        self.dropbot_actor.process_task.send({"name": "poll_voltage",
                                              "args": [],
                                              "kwargs": {}})

    def set_voltage(self, voltage: int):
        print(f"Attempting to send set_voltage command to queue")
        self.dropbot_actor.process_task.send(queue_name='dropbot_actions',
                                             kwargs={"name": "set_voltage",
                                              "args": [voltage],
                                              "kwargs": {}})

    def set_frequency(self, frequency: int):
        self.dropbot_actor.process_task.send({"name": "set_frequency",
                                              "args": [frequency],
                                              "kwargs": {}})

    def set_hv(self, on: bool):
        self.dropbot_actor.process_task.send({"name": "set_hv",
                                              "args": [on],
                                              "kwargs": {}})

    def get_channels(self):
        self.dropbot_actor.process_task.send({"name": "get_channels",
                                              "args": [],
                                              "kwargs": {}})

    def set_channels(self, channels):
        self.dropbot_actor.process_task.send({"name": "set_channels",
                                              "args": [channels],
                                              "kwargs": {}})

    def set_channel_single(self, channel: int, state: bool):
        self.dropbot_actor.process_task.send({"name": "set_channel_single",
                                              "args": [channel, state],
                                              "kwargs": {}})

    def droplet_search(self, threshold: float = 0):
        self.dropbot_actor.process_task.send({"name": "droplet_search",
                                              "args": [threshold],
                                              "kwargs": {}})

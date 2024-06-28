import dramatiq
from traits.api import Interface


class IDropbotControllerService(Interface):

    def create_actor_wrappers(self):
        pass

    def start_device_monitoring(self, hwids_to_check):
        pass

    def on_dropbot_port_found(self, event):
        pass

    def connect_to_dropbot(self, port_name):
        pass

    def on_no_power(self):
        pass

    def setup_dropbot(self):
        pass

    def output_state_changed_wrapper(self, signal: dict[str, str]):
        pass

    def halted_event_wrapper(self):
        pass

    def capacitance_updated_wrapper(self, signal: dict[str, str]):
        pass

    def on_disconnected(self):
        pass

    def create_dropbot_backend_listener_actor(self):
        pass

    def detect_shorts(self):
        pass

    def check_halted(self):
        pass

    def actuate(self, message):
        pass

    def droplet_search(self, current_state, threshold: float = 0):
        pass

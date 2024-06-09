# eventhub_services.py
from traits.api import HasTraits, provides

from ..plugins.control_plugins.event_hub import EventHubActor
from ..interfaces.i_event_hub_service import IEventHubService
from ..utils.logger import initialize_logger

logger = initialize_logger(__name__)


@provides(IEventHubService)
class EventHubService(HasTraits):
    def __init__(self):
        super().__init__()
        self.event_hub_actor = EventHubActor()

    def send_task(self, interface_name, service_name, task_name, args, kwargs):
        logger.debug(
            f"Sending task '{task_name}' to service '{service_name}' from interface '{interface_name}' with args: {args} and kwargs: {kwargs}")
        self.event_hub_actor.process_task.send(
            {"interface_name": interface_name, "service_name": service_name, "task_name": task_name, "args": args,
             "kwargs": kwargs})

    def _get_service(self, service_interface):
        return self.application.get_service(service_interface)

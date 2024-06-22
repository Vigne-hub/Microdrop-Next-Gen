from traits.has_traits import Interface
from traits.trait_types import Str


class IDropbotService(Interface):

    # task_name
    id = Str

    # define payload
    payload_model = Str

    # response_queue_id

    def process_task(self, task_info):
        """Run analysis on the given data and return the result."""


from traits.api import Interface, Str




class ILoggingService(Interface):
    def log(self, message):
        """Log the given message."""


class IAnalysisService(Interface):

    # task_name
    id = Str

    # define payload
    payload_model = Str

    # response_queue_id

    def process_task(self, task_info):
        """Run analysis on the given data and return the result."""
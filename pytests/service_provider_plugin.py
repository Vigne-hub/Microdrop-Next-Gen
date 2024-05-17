from traits.api import HasTraits
from traits.has_traits import provides
import json
import time
import dramatiq
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

##### Each of these services would need to have a model to define their payload which can be imported to use this service ####

@provides(IAnalysisService)
class AnalysisService(HasTraits):

    # task_name
    id = Str

    # define payload
    payload_model = Str('{"args_to_sum": []}')

    @staticmethod
    def process_task(task_info):
        print(f"Received task: {task_info}, processing in backend...")
        # Deserialize the task info from JSON
        task_data = json.loads(task_info)
        parameters = task_data.get('args_to_sum')
        time.sleep(2)
        result = sum(parameters)
        print("Analysis result:", result)
        return result


@provides(IAnalysisService)
class DramatiqAnalysisService(HasTraits):

    # task_name
    id = Str

    # define payload
    payload_model = Str('{"args_to_sum": []}')

    @dramatiq.actor(store_results=True)
    def process_task(task_info):
        return 42
        print(f"Received task: {task_info}, processing in backend...")
        # Deserialize the task info from JSON
        task_data = json.loads(task_info)
        parameters = task_data.get('args_to_sum')
        time.sleep(5)
        result = sum(parameters)
        print("Analysis result:", result)
        return result


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

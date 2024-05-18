from traits.api import HasTraits, Str
from traits.has_traits import provides
from ..Interfaces import IAnalysisService, ILoggingService
import json
import time
import dramatiq


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

    @dramatiq.actor
    def process_task(task_info):
        print(f"Received task: {task_info}, processing in backend...")
        # Deserialize the task info from JSON
        task_data = json.loads(task_info)
        parameters = task_data.get('args_to_sum')
        time.sleep(2)
        result = sum(parameters)
        print("Analysis result:", result)
        with open("results.txt", "a") as f:
            f.write(f"Analysis result: {result}\n")
        return result


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

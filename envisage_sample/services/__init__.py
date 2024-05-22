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
        parameters = task_info['args_to_sum']
        time.sleep(task_info["sleep_time"])
        result = sum(parameters)
        print("Analysis result:", result)
        return result


@provides(IAnalysisService)
class DramatiqAnalysisService(HasTraits):

    # task_name
    id = Str

    # define payload
    payload_model = Str('{"args_to_sum": [], "sleep_time": 2, "reply": 1}')

    @dramatiq.actor
    def process_task(task_info):
        print(f"Received task: {task_info}, processing in backend...")

        # get args from task_info
        time_sleep = task_info.get("sleep_time", 2)
        args_to_sum = task_info.get("args_to_sum", [0])
        reply = task_info.get("reply", 1)
        results_file = task_info.get("results_file", "results.txt")

        time.sleep(time_sleep)
        result = sum(args_to_sum)

        print("Analysis result:", result)
        with open(results_file, "a") as f:
            f.write(f"Analysis result: {result}\n")

        if reply:
            return result


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

import time

import dramatiq
from traits.has_traits import provides, HasTraits
from traits.trait_types import Str

from ..interfaces.i_analysis_service import IAnalysisService


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

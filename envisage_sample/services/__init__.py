import dramatiq
from traits.api import HasTraits, Str
from traits.has_traits import provides
from envisage_sample.Interfaces import IAnalysisService, ILoggingService
from envisage_sample.services.dramatiq_tasks import process_task



##### Each of these services would need to have a model to define their payload which can be imported to use this service ####

@provides(IAnalysisService)
class AnalysisService(HasTraits):
    # define payload
    payload_model = Str

    def process_task(self, task_info):
        print(f"Task has been sent to Dramatiq.")
        process_task.send(task_info)


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

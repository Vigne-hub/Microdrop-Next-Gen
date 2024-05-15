from traits.has_traits import provides

from envisage_sample.Interfaces import IAnalysisService, ILoggingService


@provides(IAnalysisService)
class AnalysisService:
    def run_analysis(self, data):
        print(f"Running analysis on {data}")
        # Perform analysis...
        return "Analysis Result"


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

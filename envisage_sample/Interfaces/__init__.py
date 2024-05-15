
from traits.api import Interface


class ILoggingService(Interface):
    def log(message):
        """Log the given message."""


class IAnalysisService(Interface):
    def run_analysis(data):
        """Run analysis on the given data and return the result."""
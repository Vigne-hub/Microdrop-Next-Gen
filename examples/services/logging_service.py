from traits.has_traits import provides

from ..interfaces.i_logging_service import ILoggingService


@provides(ILoggingService)
class LoggingService:
    def log(self, message):
        print(f"Log: {message}")

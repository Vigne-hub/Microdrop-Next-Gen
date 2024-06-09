from traits.has_traits import Interface


class ILoggingService(Interface):
    def log(self, message):
        """Log the given message."""

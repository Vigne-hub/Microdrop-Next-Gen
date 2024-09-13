from traits.api import Interface, Str, Dict


class IDropbotControlMixinService(Interface):
    """
    An interface for a dropbot control mixin that provides certain methods for a dropbot controller
    """

    id = Str
    name = Str



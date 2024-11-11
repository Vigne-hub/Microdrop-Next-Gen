from traits.api import Interface, Str


class IDropbotControlMixinService(Interface):
    """
    An interface for a dropbot control mixin that provides certain methods for a dropbot controller
    """

    id = Str
    name = Str

    ################################### Exposed Methods ###############################

    def on_topic_request(self, message):
        """
        A method that is called when a dropbot topic request is received. This naming convention is to be followed
        for methods to be exposed. While calling it one would send a message to a topic that is
        something/dropbot/topic
        """
        pass

    ####################################################################################



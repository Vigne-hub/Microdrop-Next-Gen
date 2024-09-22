from dramatiq import Actor
from traits.api import Interface, Instance


class IControllerBase(Interface):
    """
    Interface for some controller.
    Provides methods for controlling some object via dramatiq signalling.
    """

    listener = Instance(Actor, desc="Create Dramatiq actor to listen for messages to control this object.")

    def traits_init(self):
        """
        Initialize the controller: Needs to set listener to actor returned by create_listener_actor
        """
        pass

    def create_listener_actor(self) -> Actor:
        """
        Create a Dramatiq actor for listening to messages relating to controlling this object.

        Returns:
            dramatiq.Actor: The created Dramatiq actor.
        """
        pass

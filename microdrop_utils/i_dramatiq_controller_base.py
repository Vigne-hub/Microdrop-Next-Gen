from dramatiq import Actor
from traits.api import Interface, Instance


class IDramatiqControllerBase(Interface):
    """
    Interface for some controller.
    Provides methods for controlling some object via dramatiq signalling.
    """

    listener = Instance(Actor, desc="Create Dramatiq actor to listen for messages to control this object.")

    def traits_init(self):
        """
        Initialize the controller: Automatically Sets listener actor returned by _listener_default.

        Do not have to event do anything in this method. Just needs to pass.

        Could set the listener explicitly for clarity.
        """
        pass


    def _listener_default(self) -> Actor:
        """
        Create a Dramatiq actor for listening to messages relating to controlling this object.

        Returns:
            dramatiq.Actor: The created Dramatiq actor.
        """
        pass

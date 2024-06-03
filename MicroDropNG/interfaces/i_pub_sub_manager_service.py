import logging
from pydantic import BaseModel
from traits.has_traits import Interface
from traits.trait_types import Str, Callable, Any

class IPubSubManagerService(Interface):

    #: task_name
    id = Str

    #: name
    name = Str

    def create_publisher(self, publisher_name: Str, exchange_name: Str):
        """Create a publisher for a given exchange"""

    def publish(self, message: BaseModel, publisher: Str):
        """Publish a message to a given exchange"""

    def create_subscriber(self, subscriber_name: Str):
        """Create a subscriber"""

    def bind_sub_to_pub(self, subscriber: Str, exchange_name: Str):
        """Bind a subscriber to a publisher"""

    def start_consumer(self, subscriber: Str, func: Callable(Any)):
        """Start the consumer"""

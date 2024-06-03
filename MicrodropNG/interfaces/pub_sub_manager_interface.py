import logging
from typing import Callable, Any
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)


class IPubSubManagerService:

    def create_publisher(self, publisher_name: str, exchange_name: str):
        raise NotImplementedError

    def publish(self, message: BaseModel, publisher: str):
        raise NotImplementedError

    def create_subscriber(self, subscriber_name: str):
        raise NotImplementedError

    def bind_sub_to_pub(self, subscriber: str, exchange_name: str):
        raise NotImplementedError

    def start_consumer(self, subscriber: str, func: Callable[[Any, Any, Any, Any], None]):
        raise NotImplementedError

from traits.api import HasTraits, Dict, Str, List
import dramatiq
from microdrop_utils._logger import get_logger

logger = get_logger(__name__)


def publish_message(message, topic, actor_to_send="message_router_actor"):
    """
    Publish a message to a given actor with a certain topic
    """
    logger.debug(f"Publishing message: {message} to actor: {actor_to_send} on topic: {topic}")
    print(f"Publishing message: {message} to actor: {actor_to_send} on topic: {topic}")
    broker = dramatiq.get_broker()

    message = dramatiq.Message(
        queue_name="default",
        actor_name=actor_to_send,
        args=(message, topic),
        kwargs={},
        options={},
    )

    broker.enqueue(message)


class MessageRouterData(HasTraits):
    """
    A class that stores topics and their subscribers.

    Attributes:
        topic_subscriber_map (Dict): A dictionary mapping topics to a list of their subscribing actor names.
    """
    topic_subscriber_map = Dict(Str, List(Str),
                                desc="A dictionary of topics and a list of their subscribing actor names")

    def add_subscriber_to_topic(self, topic: Str, subscribing_actor_name: Str):
        """
        Adds a subscriber to a specific topic.

        Args:
            topic (str): The topic to subscribe to.
            subscribing_actor_name (str): The name of the subscribing actor.
        """
        if topic not in self.topic_subscriber_map:
            self.topic_subscriber_map[topic] = [subscribing_actor_name]
        else:
            if subscribing_actor_name not in self.topic_subscriber_map[topic]:
                self.topic_subscriber_map[topic].append(subscribing_actor_name)

    def remove_subscriber_from_topic(self, topic: Str, subscribing_actor_name: Str):
        """
        Removes a subscriber from a specific topic. If the topic has no more subscribers, it is removed from the map.

        Args:
            topic (str): The topic to unsubscribe from.
            subscribing_actor_name (str): The name of the subscribing actor.
        """
        if topic in self.topic_subscriber_map:
            self.topic_subscriber_map[topic].remove(subscribing_actor_name)
            if not self.topic_subscriber_map[topic]:
                del self.topic_subscriber_map[topic]

    def get_subscribers_for_topic(self, topic):
        """
        Gets the list of subscribers for a specific topic. A subscriber to a topic 'x' is also a subscriber to 'x.y.z',
        but a subscriber to 'x.y.z' is not a subscriber to 'x'.

        Args:
            topic (str): The topic to get subscribers for.

        Returns:
            list: A list of subscribers for the topic.
        """
        subscribers = set()
        topic_parts = topic.split('.')

        try:
            for key, value in self.topic_subscriber_map.items():
                key_parts = key.split('.')
                if len(key_parts) <= len(topic_parts) and key_parts == topic_parts[:len(key_parts)]:
                    subscribers.update(value)
        except Exception as e:
            logger.error(f"Error getting subscribers for topic: {topic}")
            logger.error(e)

        return list(subscribers)


class MessageRouterActor:
    """
    A class that routes messages to subscribers based on topics
    """

    def __init__(self, message_router_data: MessageRouterData = None):
        if message_router_data is None:
            message_router_data = MessageRouterData()

        self.message_router_data = message_router_data
        self.message_router_actor = self.create_message_router_actor()

        # We define this actor here like this since we need to access self.message_router_data but cannot have this
        # actor as a method of this class since we cannot have other processes call this with the self object.

    def create_message_router_actor(self):
        """
        Create a message router actor that routes messages to subscribers based on topics.
        """
        @dramatiq.actor
        def message_router_actor(message: Str, topic: Str):
            """
            A Dramatiq actor that routes messages to subscribers based on topics.
            """
            logger.debug(f"MESSAGE_ROUTER: Received message: {message} on topic: {topic}")

            subscribing_actor_names = self.message_router_data.get_subscribers_for_topic(topic)

            for subscribing_actor_name in subscribing_actor_names:
                logger.debug(f"MESSAGE_ROUTER: Publishing message: {message} to actor: {subscribing_actor_name}")
                publish_message(message, topic, subscribing_actor_name)

            logger.debug(
                f"MESSAGE_ROUTER: Message: {message} on topic {topic} published to {len(subscribing_actor_names)} subscribers")

        return message_router_actor

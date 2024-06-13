import pytest
import dramatiq
from .common import worker

@pytest.fixture()
def router_actor():
    """
    Fixture to initialize a MessageRouterActor instance.

    Returns:
        MessageRouterActor: An instance of MessageRouterActor.
    """
    from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import MessageRouterActor

    return MessageRouterActor()

@pytest.fixture
def router_data():
    """
    Fixture to initialize a MessageRouterData instance.

    Returns:
        MessageRouterData: An instance of MessageRouterData.
    """
    from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import MessageRouterData

    return MessageRouterData()


def test_add_subscriber_to_topic(router_data):
    """
    Test adding subscribers to a topic.

    Args:
        router_data (MessageRouterData): The message router data instance.
    """
    router_data.add_subscriber_to_topic("x", "actor1")
    assert router_data.topic_subscriber_map["x"] == ["actor1"]
    router_data.add_subscriber_to_topic("x", "actor2")
    assert router_data.topic_subscriber_map["x"] == ["actor1", "actor2"]


def test_remove_subscriber_from_topic(router_data):
    """
    Test removing subscribers from a topic.

    Args:
        router_data (MessageRouterData): The message router data instance.
    """
    router_data.add_subscriber_to_topic("x", "actor1")
    router_data.add_subscriber_to_topic("x", "actor2")
    router_data.remove_subscriber_from_topic("x", "actor1")
    assert router_data.topic_subscriber_map["x"] == ["actor2"]
    router_data.remove_subscriber_from_topic("x", "actor2")
    assert "x" not in router_data.topic_subscriber_map


def test_get_subscribers_for_topic(router_data):
    """
    Test getting subscribers for a topic.

    Args:
        router_data (MessageRouterData): The message router data instance.
    """
    router_data.add_subscriber_to_topic("x", "actor1")
    router_data.add_subscriber_to_topic("x.y", "actor2")
    router_data.add_subscriber_to_topic("x.y.z", "actor3")

    assert router_data.get_subscribers_for_topic("x") == ["actor1"]
    assert set(router_data.get_subscribers_for_topic("x.y")) == {"actor1", "actor2"}
    assert set(router_data.get_subscribers_for_topic("x.y.z")) == {"actor1", "actor2", "actor3"}
    assert router_data.get_subscribers_for_topic("nonexistent") == []


def test_message_router_actor_can_route_message(router_actor):
    from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import publish_message

    # Given that I have a database
    database = {}

    # And an actor that can write data to that database
    @dramatiq.actor
    def put(message, topic):
        database[topic] = message

    test_topic = "test_topic"
    test_message = "test_message"

    # after declaring the actor, I add it to the message router and ascribe an topic to it that it will listen to.
    router_actor.message_router_data.add_subscriber_to_topic(topic=test_topic, subscribing_actor_name="put")

    # Now I publish a message to the message router actor to the test topic for triggering it.
    publish_message(test_message, test_topic, "message_router_actor")

    # And I give the workers time to process the messages
    with worker(dramatiq.get_broker(), worker_timeout=1000):
        dramatiq.get_broker().join("default")

    # I expect the database to be populated
    assert database == {test_topic: test_message}


def test_message_router_actor_can_route_message_to_multiple_subscribing_actors(router_actor):
    from examples.dramatiq_pub_sub_ui.dramatiq_pub_sub_helpers import publish_message

    # Given that I have two databases
    database1 = {}
    database2 = {}

    # And actors that can write data to these databases
    @dramatiq.actor
    def put1(message, topic):
        database1[topic] = message

    @dramatiq.actor
    def put2(message, topic):
        database2[topic] = message

    test_topic = "test_topic"
    test_message = "test_message"

    # after declaring the actors, I add to the message router and ascribe topics.
    router_actor.message_router_data.add_subscriber_to_topic(topic=test_topic, subscribing_actor_name="put1")
    router_actor.message_router_data.add_subscriber_to_topic(topic=test_topic + ".y", subscribing_actor_name="put2")

    # Now I publish a message to the message router actor to the test topic for triggering it.
    publish_message(test_message, test_topic, "message_router_actor")
    # this should only trigger the one actor that is subscribed to the topic

    # Now I publish a message to the message router actor to the test topic.y for triggering it.
    publish_message(test_message, test_topic + ".y", "message_router_actor")
    # this should trigger the two actors that are subscribed to the topic and the topic.y (the subtopic)

    # And I give the workers time to process the messages
    with worker(dramatiq.get_broker(), worker_timeout=1):
        dramatiq.get_broker().join("default")

    # I expect the database to be populated like so
    assert database1[test_topic] == test_message
    assert database1[test_topic + ".y"] == test_message
    assert database2[test_topic + ".y"] == test_message


if __name__ == "__main__":
    pytest.main()
